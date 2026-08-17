#!/usr/bin/env python3
"""ARC-AGI-3 paired MINI-PILOT driver.

The committed state is preparation-only. ``dry-run`` uses only in-process
stubs. ``live`` fails closed unless both frozen manifest booleans and a
separate owner-only authorization receipt are true.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

ARMS = ("jcode-native", "jcode-azdaja")
ACTIONS = frozenset({"RESET", *(f"ACTION{i}" for i in range(1, 8))})
SAFE_ID = re.compile(r"[a-z0-9][a-z0-9-]{1,31}\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
GIT_COMMIT = re.compile(r"[0-9a-f]{40}\Z")
HISTORY_MODE = 0o600
DIRECTORY_MODE = 0o700
DRY_GAME = "ls20"


class GateError(RuntimeError):
    """A deterministic preflight/runtime gate failed."""


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise GateError(f"cannot read JSON object {path.name}: {type(exc).__name__}") from exc
    if not isinstance(value, dict):
        raise GateError(f"{path.name} is not a JSON object")
    return value


def verify_manifest(path: Path) -> tuple[dict[str, Any], str]:
    data = path.read_bytes()
    digest = sha256_bytes(data)
    sidecar = path.with_suffix(".sha256")
    fields = sidecar.read_text(encoding="ascii").strip().split()
    if len(fields) != 2 or fields[0] != digest or fields[1] != path.name:
        raise GateError("manifest sidecar mismatch")
    manifest = read_json_object(path)
    if manifest.get("schema_version") != 1:
        raise GateError("unsupported manifest schema")
    suite = manifest.get("suite")
    games = manifest.get("games")
    if not isinstance(suite, dict) or not isinstance(games, list) or len(games) != 5:
        raise GateError("manifest must freeze exactly five games")
    ids: list[str] = []
    dry_count = 0
    for game in games:
        if not isinstance(game, dict):
            raise GateError("game entry is not an object")
        game_id = game.get("game_id")
        baselines = game.get("human_level_baseline_actions")
        if not isinstance(game_id, str) or not SAFE_ID.fullmatch(game_id):
            raise GateError("invalid game id")
        if game_id in ids:
            raise GateError("duplicate game id")
        ids.append(game_id)
        if not isinstance(baselines, list) or not baselines or any(type(item) is not int or item <= 0 for item in baselines):
            raise GateError(f"{game_id}: invalid human baseline")
        human_total = sum(baselines)
        if game.get("official_human_actions_total") != human_total:
            raise GateError(f"{game_id}: human total drift")
        level_caps = game.get("level_action_caps")
        expected_level_caps = [5 * item for item in baselines]
        if (
            game.get("action_cap_multiplier") != 5
            or level_caps != expected_level_caps
            or game.get("max_actions") != sum(expected_level_caps)
        ):
            raise GateError(f"{game_id}: per-level/total action cap is not exactly 5x human baseline")
        if game.get("dry_run_stub") is True:
            dry_count += 1
            if game_id != DRY_GAME:
                raise GateError("unexpected dry-run game")
    if ids != suite.get("game_order") or suite.get("pair_order") != list(ARMS):
        raise GateError("frozen game or pair order drift")
    if dry_count != 1:
        raise GateError("exactly one dry-run game must be selected")
    common = manifest.get("common_live_model_config")
    treatment = manifest.get("treatment_only")
    if not isinstance(common, dict) or not isinstance(treatment, dict):
        raise GateError("missing model/treatment config")
    if not isinstance(common.get("jcode_binary_sha256"), str) or not SHA256.fullmatch(common["jcode_binary_sha256"]):
        raise GateError("invalid jcode_binary_sha256")
    if not isinstance(common.get("jcode_source_commit"), str) or not GIT_COMMIT.fullmatch(common["jcode_source_commit"]):
        raise GateError("invalid jcode_source_commit")
    hashes = treatment.get("azdaja_binary_sha256")
    if not isinstance(hashes, dict) or set(hashes) != {"darwin-arm64", "linux-x86_64"}:
        raise GateError("Azdaja platform identity drift")
    if any(not isinstance(item, str) or not SHA256.fullmatch(item) for item in hashes.values()):
        raise GateError("invalid Azdaja digest")
    if treatment.get("trigger_completed_turns") != 2 or treatment.get("max_skill_invocations_per_game") != 1:
        raise GateError("treatment trigger drift")
    return manifest, digest


def manifest_game(manifest: dict[str, Any], game_id: str) -> dict[str, Any]:
    matches = [item for item in manifest["games"] if item["game_id"] == game_id]
    if len(matches) != 1:
        raise GateError(f"manifest lacks unique game {game_id}")
    return matches[0]


def owner_file_assertion(fd: int, *, expected_identity: tuple[int, int] | None = None) -> tuple[int, int]:
    metadata = os.fstat(fd)
    if not stat.S_ISREG(metadata.st_mode) or stat.S_IMODE(metadata.st_mode) != HISTORY_MODE:
        raise GateError("turn history is not an owner-only regular file")
    if hasattr(os, "geteuid") and metadata.st_uid != os.geteuid():
        raise GateError("turn history owner mismatch")
    if metadata.st_nlink != 1:
        raise GateError("turn history must have exactly one link")
    identity = (metadata.st_dev, metadata.st_ino)
    if expected_identity is not None and identity != expected_identity:
        raise GateError("turn history identity changed")
    return identity


class OwnerHistory:
    def __init__(self, directory: Path) -> None:
        self.path = directory / "turn-history.jsonl"
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
        self.fd = os.open(self.path, flags, HISTORY_MODE)
        os.chmod(self.path, HISTORY_MODE)
        self.identity = owner_file_assertion(self.fd)
        self.records = 0

    def _read_bound_path(self) -> bytes:
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(self.path, flags)
        try:
            owner_file_assertion(fd, expected_identity=self.identity)
            blocks: list[bytes] = []
            while True:
                block = os.read(fd, 65536)
                if not block:
                    break
                blocks.append(block)
            return b"".join(blocks)
        finally:
            os.close(fd)

    def append(self, value: dict[str, Any]) -> None:
        owner_file_assertion(self.fd, expected_identity=self.identity)
        self._read_bound_path()
        data = canonical_bytes(value) + b"\n"
        offset = 0
        while offset < len(data):
            offset += os.write(self.fd, data[offset:])
        os.fsync(self.fd)
        self.records += 1

    def digest(self) -> tuple[str, int]:
        owner_file_assertion(self.fd, expected_identity=self.identity)
        data = self._read_bound_path()
        return sha256_bytes(data), len(data)

    def close(self) -> None:
        if self.fd >= 0:
            os.close(self.fd)
            self.fd = -1


@dataclass(frozen=True)
class Observation:
    game_id: str
    state: str
    levels_completed: int
    win_levels: int
    available_actions: tuple[str, ...]
    public_state: dict[str, Any]

    def state_digest(self) -> str:
        return sha256_bytes(canonical_bytes({
            "game_id": self.game_id,
            "state": self.state,
            "levels_completed": self.levels_completed,
            "public_state": self.public_state,
        }))

    def history_value(self) -> dict[str, Any]:
        return {
            "game_id": self.game_id,
            "state": self.state,
            "levels_completed": self.levels_completed,
            "win_levels": self.win_levels,
            "available_actions": list(self.available_actions),
            "observation": self.public_state,
        }


@dataclass(frozen=True)
class Action:
    name: str
    data: dict[str, int]

    def __post_init__(self) -> None:
        if self.name not in ACTIONS:
            raise GateError(f"invalid action {self.name!r}")
        if self.name == "ACTION6":
            if set(self.data) != {"x", "y"} or any(type(self.data[key]) is not int or not 0 <= self.data[key] <= 63 for key in ("x", "y")):
                raise GateError("ACTION6 requires integer x/y in [0,63]")
        elif self.data:
            raise GateError(f"{self.name} must not carry action data")


class Game(Protocol):
    @property
    def observation(self) -> Observation: ...
    def step(self, action: Action) -> Observation: ...
    def close(self) -> None: ...


class Model(Protocol):
    calls: int
    def choose(self, observation: Observation, *, turn: int, history_path: Path, advisory: str | None) -> Action: ...
    def close(self) -> None: ...


class Skill(Protocol):
    invocations: int
    def analyze(self, history_path: Path, expected_identity: tuple[int, int]) -> str: ...


class StubArcadeGame:
    """Tiny deterministic simulation labelled with one public game id.

    It is not an ARC environment and never opens a socket. The toy state has a
    left boundary at 0 and a goal at 2, exposing only ACTION3/ACTION4.
    """

    def __init__(self, game_id: str) -> None:
        if game_id != DRY_GAME:
            raise GateError("stub permits exactly one public game id")
        self.position = 0
        self.closed = False
        self._observation = self._make_observation()

    def _make_observation(self) -> Observation:
        won = self.position == 2
        return Observation(
            game_id=DRY_GAME,
            state="WIN" if won else "NOT_FINISHED",
            levels_completed=1 if won else 0,
            win_levels=7,
            available_actions=() if won else ("ACTION3", "ACTION4"),
            public_state={"stub": True, "position": self.position, "goal": 2},
        )

    @property
    def observation(self) -> Observation:
        return self._observation

    def step(self, action: Action) -> Observation:
        if self.closed:
            raise GateError("step after close")
        if action.name not in self._observation.available_actions:
            raise GateError("stub received unavailable action")
        if action.name == "ACTION3":
            self.position = max(0, self.position - 1)
        else:
            self.position = min(2, self.position + 1)
        self._observation = self._make_observation()
        return self._observation

    def close(self) -> None:
        self.closed = True




class StubArcade:
    """In-process stand-in for the official Arcade.make surface."""

    def __init__(self) -> None:
        self.make_calls = 0
        self.game_ids: list[str] = []

    def make(self, game_id: str, *, seed: int = 0, **options: Any) -> StubArcadeGame:
        if seed != 0 or options:
            raise GateError("stub Arcade accepts only the frozen seed and no live options")
        self.make_calls += 1
        self.game_ids.append(game_id)
        return StubArcadeGame(game_id)


class StubJcodeModel:
    """One deterministic model implementation shared by both arms."""

    def __init__(self) -> None:
        self.calls = 0

    def choose(self, observation: Observation, *, turn: int, history_path: Path, advisory: str | None) -> Action:
        del observation, history_path
        self.calls += 1
        # Native explores a known-left boundary for 24 turns. Once the same
        # deterministic model receives the treatment advisory it moves right.
        if advisory == "prefer ACTION4" or turn > 24:
            return Action("ACTION4", {})
        return Action("ACTION3", {})

    def close(self) -> None:
        return


class StubAzdajaSkill:
    def __init__(self) -> None:
        self.invocations = 0
        self.last_input_sha256: str | None = None

    def analyze(self, history_path: Path, expected_identity: tuple[int, int]) -> str:
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(history_path, flags)
        try:
            owner_file_assertion(fd, expected_identity=expected_identity)
            data = b""
            while True:
                block = os.read(fd, 65536)
                if not block:
                    break
                data += block
        finally:
            os.close(fd)
        rows = [json.loads(line) for line in data.decode("utf-8").splitlines()]
        turns = [row for row in rows if row.get("record_type") == "turn"]
        if len(turns) < 2:
            raise GateError("stub skill triggered before history accumulated")
        self.invocations += 1
        self.last_input_sha256 = sha256_bytes(data)
        return "prefer ACTION4"


class LiveAzdajaSkill:
    def __init__(self, binary: Path, config: dict[str, Any], expected_sha256: str, env: dict[str, str]) -> None:
        if sha256_bytes(binary.read_bytes()) != expected_sha256:
            raise GateError("Azdaja binary digest mismatch")
        self.binary = binary
        self.config = config
        self.env = env
        self.invocations = 0
        self.last_input_sha256: str | None = None

    def analyze(self, history_path: Path, expected_identity: tuple[int, int]) -> str:
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(history_path, flags)
        try:
            owner_file_assertion(fd, expected_identity=expected_identity)
            data = b""
            while True:
                block = os.read(fd, 65536)
                if not block:
                    break
                data += block
        finally:
            os.close(fd)
        self.last_input_sha256 = sha256_bytes(data)
        question = self.config["skill_question"]
        completed = subprocess.run(
            [str(self.binary), "solo", question, "-f", str(history_path), "--model", self.config["root_model"], "--sub-model", self.config["sub_model"]],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=self.env,
            timeout=300,
            check=False,
        )
        if completed.returncode != 0:
            raise GateError("Azdaja skill process failed")
        verify_fd = os.open(history_path, flags)
        try:
            owner_file_assertion(verify_fd, expected_identity=expected_identity)
            after_blocks: list[bytes] = []
            while True:
                block = os.read(verify_fd, 65536)
                if not block:
                    break
                after_blocks.append(block)
        finally:
            os.close(verify_fd)
        if b"".join(after_blocks) != data:
            raise GateError("Azdaja skill modified its owner-only input")
        advisory = completed.stdout.strip()
        if not advisory or len(advisory) > 4096:
            raise GateError("Azdaja advisory is empty or oversized")
        self.invocations += 1
        return advisory


def ndjson_response(text: str) -> str:
    assembled = ""
    completed = ""
    for line in text.splitlines():
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(value, dict):
            continue
        kind = value.get("type") or value.get("ev")
        if kind in {"text_delta", "assistant_text_delta"} and isinstance(value.get("text"), str):
            assembled += value["text"]
        for key in ("response", "output_text", "text", "content"):
            item = value.get(key)
            if kind in {"result", "message_end", "assistant", "final", "done"} and isinstance(item, str):
                completed = item
    return completed or assembled


class LiveJcodeModel:
    def __init__(self, binary: Path, config: dict[str, Any], expected_sha256: str, env: dict[str, str]) -> None:
        if sha256_bytes(binary.read_bytes()) != expected_sha256:
            raise GateError("Jcode binary digest mismatch")
        self.binary = binary
        self.config = config
        self.env = env
        self.calls = 0

    def choose(self, observation: Observation, *, turn: int, history_path: Path, advisory: str | None) -> Action:
        prompt = canonical_bytes({
            "contract": "Return exactly one JSON object: action is RESET or ACTION1..ACTION7; data is {} except ACTION6 requires integer x,y in 0..63.",
            "turn": turn,
            "owner_turn_history_file": str(history_path),
            "current_observation": observation.history_value(),
            "azdaja_advisory": advisory,
        }).decode("utf-8")
        command = [
            str(self.binary), "run", "--ndjson", "--trace", "--no-update", "--no-selfdev", "--quiet",
            "--provider", self.config["provider"], "--model", self.config["model"],
            "--tool-profile", self.config["tool_profile"], "--tools", ",".join(self.config["tools"]),
            "--cwd", str(history_path.parent), prompt,
        ]
        completed = subprocess.run(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=self.env, timeout=300, check=False)
        if completed.returncode != 0:
            raise GateError("Jcode action process failed")
        raw = ndjson_response(completed.stdout).strip()
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise GateError("Jcode action is not exact JSON") from exc
        if not isinstance(value, dict) or set(value) != {"action", "data"} or not isinstance(value["action"], str) or not isinstance(value["data"], dict):
            raise GateError("Jcode action JSON has wrong shape")
        self.calls += 1
        return Action(value["action"], value["data"])

    def close(self) -> None:
        subprocess.run(
            [str(self.binary), "server", "stop", "--force", "--json", "--no-update", "--no-selfdev"],
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            env=self.env, timeout=20, check=False,
        )


def public_frame_value(raw: Any) -> dict[str, Any]:
    frame = getattr(raw, "frame", [])
    normalized: list[Any] = []
    for item in frame or []:
        normalized.append(item.tolist() if hasattr(item, "tolist") else item)
    return {"frame": normalized, "full_reset": bool(getattr(raw, "full_reset", False))}


class LiveArcadeGame:
    def __init__(self, game_id: str, api_key: str) -> None:
        # This import and every Arcade operation are unreachable in the frozen
        # prep state because authorization is checked first.
        try:
            import arc_agi  # type: ignore
            from arcengine import GameAction  # type: ignore
        except ImportError as exc:
            raise GateError("official arc-agi toolkit is not installed") from exc
        self.GameAction = GameAction
        self.arcade = arc_agi.Arcade(arc_api_key=api_key, operation_mode=arc_agi.OperationMode.ONLINE)
        self.env = self.arcade.make(game_id, seed=0, save_recording=False, include_frame_data=True, render_mode=None)
        if self.env is None:
            raise GateError("Arcade.make returned no environment")
        self.game_id = game_id
        self._observation = self._convert(self.env.observation_space)

    def _convert(self, raw: Any) -> Observation:
        if raw is None:
            raise GateError("Arcade returned no frame")
        raw_actions = getattr(raw, "available_actions", []) or getattr(self.env, "action_space", [])
        action_names = []
        for item in raw_actions:
            action_names.append(item.name if hasattr(item, "name") else self.GameAction.from_id(item).name)
        actions = tuple(sorted(action_names))
        state = getattr(raw, "state", "UNKNOWN")
        state_name = state.name if hasattr(state, "name") else str(state)
        return Observation(
            game_id=self.game_id,
            state=state_name,
            levels_completed=int(getattr(raw, "levels_completed", 0)),
            win_levels=int(getattr(raw, "win_levels", 0)),
            available_actions=actions,
            public_state=public_frame_value(raw),
        )

    @property
    def observation(self) -> Observation:
        return self._observation

    def step(self, action: Action) -> Observation:
        enum_action = getattr(self.GameAction, action.name)
        self._observation = self._convert(self.env.step(enum_action, data=action.data))
        return self._observation

    def close(self) -> None:
        close = getattr(self.env, "close", None)
        if callable(close):
            close()
        close_card = getattr(self.arcade, "close_scorecard", None)
        if callable(close_card):
            close_card()


def shadow_rhae(human_baselines: list[int], agent_actions: list[int]) -> float:
    if len(agent_actions) > len(human_baselines) or any(type(item) is not int or item <= 0 for item in agent_actions):
        raise GateError("invalid per-level agent action counts")
    denominator = sum(range(1, len(human_baselines) + 1))
    numerator = 0.0
    for index, count in enumerate(agent_actions):
        numerator += (index + 1) * min((human_baselines[index] / count) ** 2, 1.15)
    value = numerator / denominator
    if not math.isfinite(value) or not 0 <= value <= 1.15:
        raise GateError("invalid shadow RHAE")
    return value


def run_arm(
    *,
    arm: str,
    game_id: str,
    game_config: dict[str, Any],
    common_config: dict[str, Any],
    treatment_config: dict[str, Any],
    game: Game,
    model: Model,
    skill: Skill | None,
    root: Path,
) -> dict[str, Any]:
    if arm not in ARMS or (arm == "jcode-native") != (skill is None):
        raise GateError("arm/skill binding mismatch")
    os.chmod(root, DIRECTORY_MODE)
    history = OwnerHistory(root)
    cleanup_errors: list[str] = []
    action_counts: Counter[str] = Counter()
    seen_states = {game.observation.state_digest()}
    known_controls: set[tuple[str, str, bytes]] = set()
    revisited_states = 0
    repeated_known_controls = 0
    completed_turns = 0
    level_start_action = 0
    level_action_counts: list[int] = []
    previous_levels = game.observation.levels_completed
    persisted_advisory: str | None = None
    skill_input_sha256: str | None = None
    trajectory_hasher = hashlib.sha256()
    status = "running"
    try:
        history.append({"record_type": "start", "observation": game.observation.history_value()})
        max_actions = game_config["max_actions"]
        level_action_caps = game_config["level_action_caps"]
        termination_reason = "GAME_WIN"
        while game.observation.state != "WIN" and completed_turns < max_actions:
            current_level = game.observation.levels_completed
            if current_level >= len(level_action_caps):
                raise GateError("non-winning frame is beyond the frozen level cap table")
            if completed_turns - level_start_action >= level_action_caps[current_level]:
                termination_reason = "ACTION_BUDGET"
                break
            if (
                skill is not None
                and skill.invocations < treatment_config["max_skill_invocations_per_game"]
                and completed_turns == treatment_config["trigger_completed_turns"]
            ):
                persisted_advisory = skill.analyze(history.path, history.identity)
                skill_input_sha256 = getattr(skill, "last_input_sha256", None)
            before = game.observation
            forced_reset = before.state in {"GAME_OVER", "NOT_PLAYED"}
            if forced_reset:
                action = Action("RESET", {})
            else:
                history_before_model = history.digest()
                action = model.choose(before, turn=completed_turns + 1, history_path=history.path, advisory=persisted_advisory)
                if history.digest() != history_before_model:
                    raise GateError("model modified the accumulated turn history")
            if not forced_reset and action.name not in before.available_actions:
                raise GateError("model selected unavailable action")
            control = (before.state_digest(), action.name, canonical_bytes(action.data))
            if control in known_controls:
                repeated_known_controls += 1
            else:
                known_controls.add(control)
            after = game.step(action)
            completed_turns += 1
            action_counts[action.name] += 1
            after_digest = after.state_digest()
            if after_digest in seen_states:
                revisited_states += 1
            else:
                seen_states.add(after_digest)
            row = {
                "record_type": "turn",
                "turn": completed_turns,
                "before_state_sha256": before.state_digest(),
                "action": {"name": action.name, "data": action.data},
                "after": after.history_value(),
            }
            history.append(row)
            trajectory_hasher.update(canonical_bytes(row) + b"\n")
            if after.levels_completed > previous_levels:
                if after.levels_completed != previous_levels + 1:
                    raise GateError("levels completed skipped")
                level_action_counts.append(completed_turns - level_start_action)
                level_start_action = completed_turns
                previous_levels = after.levels_completed
        if game.observation.state != "WIN":
            termination_reason = "ACTION_BUDGET"
        expected_skill_calls = 0 if arm == "jcode-native" else 1
        actual_skill_calls = 0 if skill is None else skill.invocations
        if actual_skill_calls != expected_skill_calls:
            raise GateError("skill invocation count drift")
        history_sha256, history_bytes = history.digest()
        score = shadow_rhae(game_config["human_level_baseline_actions"], level_action_counts)
        status = "complete" if termination_reason == "GAME_WIN" else "action_budget"
        return {
            "arm": arm,
            "game_id": game_id,
            "status": status,
            "termination_reason": termination_reason,
            "common_model_config_sha256": sha256_bytes(canonical_bytes(common_config)),
            "level_action_caps": level_action_caps,
            "action_cap": max_actions,
            "actions": completed_turns,
            "actions_by_name": dict(sorted(action_counts.items())),
            "completed_levels": len(level_action_counts),
            "agent_actions_per_completed_level": level_action_counts,
            "shadow_rhae_fraction": score,
            "wasted_actions": {
                "revisited_states": revisited_states,
                "repeated_known_controls": repeated_known_controls,
            },
            "game_adapter": "arcade-api-game-stub-v1" if isinstance(game, StubArcadeGame) else "official-arcade-online-v1",
            "model_adapter": "deterministic-stub-v1" if isinstance(model, StubJcodeModel) else "jcode-live-v1",
            "model_calls": model.calls,
            "skill_adapter": None if skill is None else ("deterministic-stub-v1" if isinstance(skill, StubAzdajaSkill) else "azdaja-live-v1"),
            "skill_invocations": actual_skill_calls,
            "skill_input_contract_asserted": skill is None or skill_input_sha256 is not None,
            "skill_input_history_sha256": skill_input_sha256,
            "history": {
                "records": history.records,
                "bytes": history_bytes,
                "sha256": history_sha256,
                "owner_only_mode_asserted": True,
                "single_link_asserted": True,
            },
            "trajectory_sha256": trajectory_hasher.hexdigest(),
        }
    finally:
        try:
            history.close()
        except OSError as exc:
            cleanup_errors.append(type(exc).__name__)
        try:
            model.close()
        except Exception as exc:  # cleanup result is fail-closed below
            cleanup_errors.append(type(exc).__name__)
        try:
            game.close()
        except Exception as exc:
            cleanup_errors.append(type(exc).__name__)
        if cleanup_errors:
            raise GateError("arm cleanup failed: " + ",".join(cleanup_errors))


def stage_active_jcode_oauth(owner_home: Path, destination_jcode_home: Path) -> None:
    source_path = owner_home / ".jcode" / "openai-auth.json"
    source_fd = os.open(source_path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    try:
        owner_file_assertion(source_fd)
        blocks: list[bytes] = []
        while True:
            block = os.read(source_fd, 65536)
            if not block:
                break
            blocks.append(block)
        value = json.loads(b"".join(blocks).decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise GateError("owner Jcode OAuth record is invalid JSON") from exc
    finally:
        os.close(source_fd)
    if not isinstance(value, dict):
        raise GateError("owner Jcode OAuth record is not an object")
    source = value
    accounts = source.get("openai_accounts")
    active = source.get("active_openai_account")
    if not isinstance(accounts, list) or not isinstance(active, str):
        raise GateError("owner Jcode OAuth metadata is invalid")
    selected = [item for item in accounts if isinstance(item, dict) and item.get("label") == active]
    if len(selected) != 1:
        raise GateError("owner Jcode active OAuth account is missing or ambiguous")
    destination_jcode_home.mkdir(mode=DIRECTORY_MODE, parents=True)
    auth_path = destination_jcode_home / "openai-auth.json"
    fd = os.open(auth_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, HISTORY_MODE)
    try:
        data = canonical_bytes({"openai_accounts": selected, "active_openai_account": active})
        os.write(fd, data)
        os.fsync(fd)
    finally:
        os.close(fd)


def install_managed_skill(binary: Path, env: dict[str, str], treatment: dict[str, Any]) -> None:
    completed = subprocess.run(
        [str(binary), "install", "--harness", "jcode"],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        timeout=60,
        check=False,
    )
    if completed.returncode != 0:
        raise GateError("provider-free managed skill installation failed")
    skill_root = Path(env["JCODE_HOME"]) / "skills" / "azdaja"
    expected = treatment["managed_skill_components_sha256"]
    for name, digest in expected.items():
        path = skill_root / name
        if not path.is_file() or sha256_bytes(path.read_bytes()) != digest:
            raise GateError(f"installed managed skill component mismatch: {name}")
    staged_binary = skill_root / "azdaja"
    expected_binary = treatment["azdaja_binary_sha256"][platform_key()]
    if not staged_binary.is_file() or sha256_bytes(staged_binary.read_bytes()) != expected_binary:
        raise GateError("installed managed skill binary mismatch")
    env["AZDAJA_CONFIG"] = str(skill_root / "config.toml")


def safe_env(base_home: Path, *, reasoning: str) -> dict[str, str]:
    env = {
        "HOME": str(base_home),
        "PATH": os.defpath,
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "JCODE_HOME": str(base_home / "jcode-home"),
        "JCODE_RUNTIME_DIR": str(base_home / "jcode-runtime"),
        "JCODE_NO_TELEMETRY": "1",
        "JCODE_RUN_MCP": "0",
        "JCODE_RUN_AUTO_POKE": "0",
        "JCODE_OPENAI_REASONING_EFFORT": reasoning,
        "AZDAJA_HOME": str(base_home / "azdaja-state"),
    }
    return env


def authorization_gate(path: Path, manifest: dict[str, Any], manifest_sha256: str) -> None:
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    try:
        owner_file_assertion(fd)
    finally:
        os.close(fd)
    value = read_json_object(path)
    required = {"experiment_id", "manifest_sha256", "track1_full_199_confirmed", "arc_live_owner_authorized"}
    if set(value) != required:
        raise GateError("authorization receipt shape drift")
    launch = manifest["launch_gate"]
    if (
        value["experiment_id"] != manifest["experiment_id"]
        or value["manifest_sha256"] != manifest_sha256
        or value["track1_full_199_confirmed"] is not True
        or value["arc_live_owner_authorized"] is not True
        or launch.get("track1_full_199_confirmed") is not True
        or launch.get("arc_live_owner_authorized") is not True
        or manifest.get("status") != "FROZEN_AUTHORIZED_FOR_LIVE_MINI"
    ):
        raise GateError("live ARC launch is not owner-authorized after Track1 full-199")


def platform_key() -> str:
    value = (platform.system(), platform.machine().lower())
    if value == ("Darwin", "arm64"):
        return "darwin-arm64"
    if value[0] == "Linux" and value[1] in {"x86_64", "amd64"}:
        return "linux-x86_64"
    raise GateError("unsupported Azdaja platform")


def run_pair(manifest: dict[str, Any], manifest_sha256: str, *, live: bool, args: argparse.Namespace) -> dict[str, Any]:
    if live:
        if args.authorization is None:
            raise GateError("live mode requires --authorization")
        authorization_gate(args.authorization, manifest, manifest_sha256)
        api_key = os.environ.get("ARC_API_KEY")
        if not api_key:
            raise GateError("ARC_API_KEY is absent")
        if args.jcode is None or args.azdaja is None:
            raise GateError("live mode requires --jcode and --azdaja")
        game_ids = manifest["suite"]["game_order"]
    else:
        api_key = ""
        game_ids = [game["game_id"] for game in manifest["games"] if game["dry_run_stub"] is True]
        if game_ids != [DRY_GAME]:
            raise GateError("dry run must select exactly one public game id")
    rows: list[dict[str, Any]] = []
    cleanup_proofs: list[bool] = []
    for game_id in game_ids:
        game_config = manifest_game(manifest, game_id)
        for arm in ARMS:
            work = Path(tempfile.mkdtemp(prefix="arc3-paired-"))
            try:
                run_root = work / "run"
                run_root.mkdir(mode=DIRECTORY_MODE)
                if live:
                    env = safe_env(work / "home", reasoning=manifest["common_live_model_config"]["reasoning_effort"])
                    Path(env["HOME"]).mkdir(mode=DIRECTORY_MODE)
                    stage_active_jcode_oauth(args.owner_home, Path(env["JCODE_HOME"]))
                    model: Model = LiveJcodeModel(args.jcode, manifest["common_live_model_config"], manifest["common_live_model_config"]["jcode_binary_sha256"], env)
                    game: Game = LiveArcadeGame(game_id, api_key)
                    skill: Skill | None = None
                    if arm == "jcode-azdaja":
                        install_managed_skill(args.azdaja, env, manifest["treatment_only"])
                        expected = manifest["treatment_only"]["azdaja_binary_sha256"][platform_key()]
                        skill = LiveAzdajaSkill(args.azdaja, manifest["treatment_only"], expected, env)
                else:
                    arcade_stub = StubArcade()
                    model = StubJcodeModel()
                    game = arcade_stub.make(game_id, seed=0)
                    if arcade_stub.make_calls != 1 or arcade_stub.game_ids != [game_id]:
                        raise GateError("stub Arcade make proof failed")
                    skill = StubAzdajaSkill() if arm == "jcode-azdaja" else None
                row = run_arm(
                    arm=arm,
                    game_id=game_id,
                    game_config=game_config,
                    common_config=manifest["common_live_model_config"],
                    treatment_config=manifest["treatment_only"],
                    game=game,
                    model=model,
                    skill=skill,
                    root=run_root,
                )
                rows.append(row)
            finally:
                shutil.rmtree(work, ignore_errors=False)
                cleanup_proofs.append(not work.exists())
    expected_rows = len(game_ids) * len(ARMS)
    if len(rows) != expected_rows or not all(cleanup_proofs):
        raise GateError("pair completion or cleanup gate failed")
    pairs: list[dict[str, Any]] = []
    for game_id in game_ids:
        selected = [row for row in rows if row["game_id"] == game_id]
        if [row["arm"] for row in selected] != list(ARMS):
            raise GateError("paired arm order drift")
        control, treatment = selected
        if control["common_model_config_sha256"] != treatment["common_model_config_sha256"] or control["action_cap"] != treatment["action_cap"]:
            raise GateError("paired model config or action cap differs")
        pairs.append({
            "game_id": game_id,
            "shadow_rhae_delta_treatment_minus_control": treatment["shadow_rhae_fraction"] - control["shadow_rhae_fraction"],
            "action_delta_treatment_minus_control": treatment["actions"] - control["actions"],
            "wasted_action_deltas_treatment_minus_control": {
                key: treatment["wasted_actions"][key] - control["wasted_actions"][key]
                for key in ("revisited_states", "repeated_known_controls")
            },
        })
    return {
        "schema_version": 1,
        "experiment_id": manifest["experiment_id"],
        "mode": "live" if live else "offline_stub_dry_run",
        "authority": "local shadow only; no absolute ARC score or leaderboard claim",
        "manifest_sha256": manifest_sha256,
        "driver_sha256": sha256_bytes(Path(__file__).read_bytes()),
        "game_ids": game_ids,
        "rows": rows,
        "paired_deltas": pairs,
        "proof": {
            "arc_live_requests": None if live else 0,
            "provider_model_inferences": None if live else 0,
            "live_tokens_spent": None if live else 0,
            "stub_model_decisions": None if live else sum(row["model_calls"] for row in rows),
            "exactly_one_public_game_stubbed": not live and game_ids == [DRY_GAME],
            "action_history_tool_rhae_cleanup_complete": True,
            "history_workspaces_removed": all(cleanup_proofs),
        },
    }


def write_output(path: Path | None, value: dict[str, Any]) -> None:
    data = json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if path is None:
        sys.stdout.write(data)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        os.write(fd, data.encode("utf-8"))
        os.fsync(fd)
    finally:
        os.close(fd)
    os.replace(temporary, path)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fail-closed ARC-AGI-3 paired driver")
    parser.add_argument("mode", choices=("preflight", "dry-run", "live"))
    parser.add_argument("--manifest", type=Path, default=Path(__file__).with_name("mini-pilot-manifest.json"))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--authorization", type=Path)
    parser.add_argument("--jcode", type=Path)
    parser.add_argument("--azdaja", type=Path)
    parser.add_argument("--owner-home", type=Path, default=Path.home())
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        manifest, digest = verify_manifest(args.manifest)
        if args.mode == "preflight":
            value = {
                "schema_version": 1,
                "status": "PREP_ONLY_LIVE_BLOCKED" if manifest["launch_gate"]["arc_live_owner_authorized"] is not True else "MANIFEST_AUTHORIZATION_FLAG_PRESENT",
                "manifest_sha256": digest,
                "five_game_manifest_valid": True,
                "dry_run_game_count": 1,
                "arc_api_key_present": bool(os.environ.get("ARC_API_KEY")),
                "network_or_model_call_made": False,
            }
        else:
            value = run_pair(manifest, digest, live=args.mode == "live", args=args)
        write_output(args.output, value)
        return 0
    except (GateError, OSError, subprocess.SubprocessError) as exc:
        print(f"blocked: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
