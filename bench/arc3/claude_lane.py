#!/usr/bin/env python3
"""Fail-closed direct Claude Code lane used by the ARC paired pilot.

This wrapper never reads ARC_API_KEY and builds a child allowlist from scratch.
Every inference gets a new process and a disposable writable cwd/state tree. On
macOS the owner HOME is exposed read-only solely so Claude Code can resolve its
subscription login; sandbox-exec denies writes outside the disposable tree.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ACTION_NAMES = ["RESET", *(f"ACTION{i}" for i in range(1, 8))]
ACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "action": {"type": "string", "enum": ACTION_NAMES},
        "data": {"type": "object"},
    },
    "required": ["action", "data"],
    "additionalProperties": False,
}
MAX_INPUT_BYTES = 8 * 1024 * 1024
MAX_OUTPUT_BYTES = 1024 * 1024


FAILURE_CATEGORIES = frozenset({
    "auth",
    "invalid_model",
    "cli_usage",
    "sandbox_permission",
    "rate_limit",
    "network",
    "other",
})


class LaneError(RuntimeError):
    def __init__(self, category: str = "other") -> None:
        self.category = category if category in FAILURE_CATEGORIES else "other"
        super().__init__(self.category)


def classify_cli_failure(stdout: bytes, stderr: bytes) -> str:
    """Map private CLI output to a fixed enum without relaying source text."""
    text = (stdout + b"\n" + stderr).decode("utf-8", errors="replace").lower()
    categories = (
        ("sandbox_permission", ("sandbox", "operation not permitted", "permission denied", "read-only file system", "not permitted")),
        ("auth", ("authentication", "unauthorized", "not logged in", "login required", "oauth", "invalid_grant", "credential", "http 401", "status 401")),
        ("invalid_model", ("invalid model", "model not found", "unknown model", "model is not available", "model unavailable", "does not have access to model")),
        ("cli_usage", ("usage:", "unknown option", "unrecognized option", "unexpected argument", "invalid argument", "requires an argument", "unknown command")),
        ("rate_limit", ("rate limit", "rate_limit", "too many requests", "http 429", "status 429", "overloaded", "capacity")),
        ("network", ("network", "connection", "connect error", "dns", "timed out", "timeout", "tls", "proxy error", "socket")),
    )
    for category, markers in categories:
        if any(marker in text for marker in markers):
            return category
    return "other"


FAILURE_ARTIFACT_MAGIC = b"ARC3_DIRECT_CLAUDE_FAILURE_V1\n"


def write_failure_artifact(path: Path, returncode: int, stdout: bytes, stderr: bytes, runtime_root: Path) -> None:
    if not path.is_absolute():
        raise LaneError("other")
    resolved_path = path.resolve(strict=False)
    resolved_runtime = runtime_root.resolve(strict=True)
    if resolved_path == resolved_runtime or resolved_runtime in resolved_path.parents:
        raise LaneError("other")
    header = (
        FAILURE_ARTIFACT_MAGIC
        + f"returncode={returncode}\nstdout_length={len(stdout)}\nstderr_length={len(stderr)}\n\n".encode("ascii")
    )
    data = header + stdout + stderr
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags, 0o600)
    except FileExistsError as exc:
        raise LaneError("other") from exc
    try:
        os.fchmod(fd, 0o600)
        offset = 0
        while offset < len(data):
            offset += os.write(fd, data[offset:])
        os.fsync(fd)
        metadata = os.fstat(fd)
        if not stat.S_ISREG(metadata.st_mode) or stat.S_IMODE(metadata.st_mode) != 0o600 or metadata.st_nlink != 1:
            raise LaneError("other")
        if hasattr(os, "geteuid") and metadata.st_uid != os.geteuid():
            raise LaneError("other")
    finally:
        os.close(fd)


def private_directory(path: Path) -> None:
    path.mkdir(mode=0o700, parents=True, exist_ok=False)
    os.chmod(path, 0o700)


def assert_executable(path: Path) -> None:
    metadata = path.stat()
    if not stat.S_ISREG(metadata.st_mode) or not os.access(path, os.X_OK):
        raise LaneError("Claude executable identity is invalid")


def child_env(owner_home: Path, call_root: Path, claude: Path) -> dict[str, str]:
    # Deliberately do not inherit the caller environment. In particular ARC_API_KEY,
    # provider API keys/tokens, hooks, settings selectors, and model selectors are absent.
    return {
        "HOME": str(owner_home),
        "PATH": str(claude.parent) + os.pathsep + os.defpath,
        "USER": os.environ.get("USER", ""),
        "LOGNAME": os.environ.get("LOGNAME", ""),
        "SHELL": os.environ.get("SHELL", "/bin/sh"),
        "TMPDIR": str(call_root / "tmp"),
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "NO_COLOR": "1",
        "CI": "1",
        "XDG_CONFIG_HOME": str(call_root / "xdg-config"),
        "XDG_CACHE_HOME": str(call_root / "xdg-cache"),
        "XDG_DATA_HOME": str(call_root / "xdg-data"),
        "CLAUDE_CODE_SAFE_MODE": "1",
        "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
    }


def sandbox_profile(call_root: Path) -> str:
    escaped = str(call_root).replace("\\", "\\\\").replace('"', '\\"')
    return (
        "(version 1)\n"
        "(allow default)\n"
        "(deny file-write*)\n"
        f"(allow file-write* (subpath \"{escaped}\"))\n"
    )


def base_command(claude: Path, *, model: str | None, structured: bool) -> list[str]:
    command = [
        str(claude),
        "--print",
        "--safe-mode",
        "--no-session-persistence",
        "--disable-slash-commands",
        "--no-chrome",
        "--strict-mcp-config",
        "--mcp-config", '{"mcpServers":{}}',
        "--settings", "{}",
        "--setting-sources", "",
        "--tools", "",
        "--permission-mode", "dontAsk",
        "--effort", "low",
        "--output-format", "json",
    ]
    if model is not None:
        # Both the outer action chooser and Ember subcalls resolve to this same
        # owner-authorized Claude Code subscription alias.
        command += ["--model", "sonnet"]
    if structured:
        command += ["--json-schema", json.dumps(ACTION_SCHEMA, separators=(",", ":"))]
    return command


def invoke(args: argparse.Namespace, prompt: bytes, *, structured: bool) -> bytes:
    if len(prompt) > MAX_INPUT_BYTES:
        raise LaneError("Claude input exceeds the local bound")
    assert_executable(args.claude)
    if not args.owner_home.is_dir() or not args.runtime_root.is_dir():
        raise LaneError("Claude lane roots are unavailable")
    call_root = Path(tempfile.mkdtemp(prefix="call-", dir=args.runtime_root))
    try:
        for name in ("cwd", "tmp", "xdg-config", "xdg-cache", "xdg-data"):
            private_directory(call_root / name)
        profile = call_root / "sandbox.sb"
        profile.write_text(sandbox_profile(call_root), encoding="utf-8")
        os.chmod(profile, 0o600)
        command = base_command(args.claude, model=args.model, structured=structured)
        if sys.platform == "darwin":
            command = ["/usr/bin/sandbox-exec", "-f", str(profile), *command]
        completed = subprocess.run(
            command,
            cwd=call_root / "cwd",
            env=child_env(args.owner_home, call_root, args.claude),
            input=prompt,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=300,
            check=False,
        )
        if completed.returncode != 0:
            if args.failure_artifact is None:
                raise LaneError("other")
            write_failure_artifact(
                args.failure_artifact,
                completed.returncode,
                completed.stdout,
                completed.stderr,
                args.runtime_root,
            )
            raise LaneError(classify_cli_failure(completed.stdout, completed.stderr))
        if len(completed.stdout) > MAX_OUTPUT_BYTES or len(completed.stderr) > MAX_OUTPUT_BYTES:
            raise LaneError("direct Claude Code output exceeds the local bound")
        return completed.stdout
    finally:
        shutil.rmtree(call_root, ignore_errors=False)


def decode_envelope(raw: bytes) -> dict[str, Any]:
    try:
        value = json.loads(raw)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise LaneError("direct Claude Code output is not JSON") from exc
    if not isinstance(value, dict):
        raise LaneError("direct Claude Code output envelope has the wrong shape")
    return value


def action(args: argparse.Namespace) -> None:
    envelope = decode_envelope(invoke(args, sys.stdin.buffer.read(), structured=True))
    value = envelope.get("structured_output")
    if value is None and isinstance(envelope.get("result"), str):
        try:
            value = json.loads(envelope["result"])
        except json.JSONDecodeError as exc:
            raise LaneError("direct Claude action result is not JSON") from exc
    if not isinstance(value, dict) or set(value) != {"action", "data"}:
        raise LaneError("direct Claude action result has the wrong shape")
    sys.stdout.write(json.dumps(value, separators=(",", ":")) + "\n")


def subcall(args: argparse.Namespace) -> None:
    envelope = decode_envelope(invoke(args, sys.stdin.buffer.read(), structured=False))
    result = envelope.get("result")
    if not isinstance(result, str) or not result.strip():
        raise LaneError("direct Claude subcall result is empty")
    sys.stdout.write(result.strip() + "\n")


def auth_check(args: argparse.Namespace) -> None:
    assert_executable(args.claude)
    if not args.owner_home.is_dir() or not args.runtime_root.is_dir():
        raise LaneError("Claude lane roots are unavailable")
    call_root = Path(tempfile.mkdtemp(prefix="auth-", dir=args.runtime_root))
    try:
        for name in ("cwd", "tmp", "xdg-config", "xdg-cache", "xdg-data"):
            private_directory(call_root / name)
        profile = call_root / "sandbox.sb"
        profile.write_text(sandbox_profile(call_root), encoding="utf-8")
        os.chmod(profile, 0o600)
        command = [str(args.claude), "auth", "status"]
        if sys.platform == "darwin":
            command = ["/usr/bin/sandbox-exec", "-f", str(profile), *command]
        completed = subprocess.run(
            command,
            cwd=call_root / "cwd",
            env=child_env(args.owner_home, call_root, args.claude),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30,
            check=False,
        )
        if completed.returncode != 0:
            category = classify_cli_failure(completed.stdout, completed.stderr)
            raise LaneError("auth" if category == "other" else category)
        # Do not relay account/auth details. Success is the entire public contract.
        sys.stdout.write("claude_subscription_auth_available\n")
    finally:
        shutil.rmtree(call_root, ignore_errors=False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Isolated direct Claude Code lane")
    parser.add_argument("mode", choices=("action", "subcall", "auth-check"))
    parser.add_argument("--claude", required=True, type=Path)
    parser.add_argument("--owner-home", required=True, type=Path)
    parser.add_argument("--runtime-root", required=True, type=Path)
    parser.add_argument("--failure-artifact", type=Path)
    parser.add_argument("--model")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.model is not None and args.model not in {"sonnet", "claude-sonnet-5"}:
            raise LaneError("Claude lane model alias drift")
        if args.mode in {"action", "subcall"} and args.failure_artifact is None:
            raise LaneError("other")
        if args.mode == "auth-check" and args.failure_artifact is not None:
            raise LaneError("other")
        if args.mode == "action":
            if args.model is None:
                raise LaneError("action mode requires a model")
            action(args)
        elif args.mode == "subcall":
            if args.model is None:
                raise LaneError("subcall mode requires a model")
            subcall(args)
        else:
            if args.model is not None:
                raise LaneError("auth-check does not accept a model")
            auth_check(args)
        return 0
    except LaneError as exc:
        print(f"blocked: direct_claude_failure={exc.category}", file=sys.stderr)
        return 2
    except (OSError, subprocess.SubprocessError):
        print("blocked: direct_claude_failure=other", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
