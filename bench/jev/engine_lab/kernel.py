"""A staged, explicit typed-judgment kernel. No credentials, HTTP or CLI entry.

Backends are injected by trusted host code. The manifest can select only an
already registered profile, never commands, paths, endpoints or larger budgets.
The cache is instance-local raw evidence reuse, not independent corroboration.
"""
from dataclasses import dataclass
import hashlib
import re
from typing import Callable
import uuid

from ..adapter import (AdapterError, canonical_bytes, strict_json_loads,
                       validate_questions, validate_response)

HEX = re.compile(r"[0-9a-f]{64}\Z")
NAME = re.compile(r"[A-Za-z0-9_-]{1,128}\Z")
MODEL = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:/-]{0,127}\Z")
MAX_MANIFEST_BYTES = 262144
MAX_REQUEST_BYTES = 32768
MAX_RESPONSE_BYTES = 32768
MAX_JOBS = 128


def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def clone(value):
    return strict_json_loads(canonical_bytes(value))


class EngineError(ValueError):
    def __init__(self, code, *, partial=None):
        super().__init__(code)
        self.partial = clone(partial or [])


@dataclass(frozen=True)
class Profile:
    model: str
    contract: str
    evaluate: Callable

    def __post_init__(self):
        if (not isinstance(self.model, str) or not MODEL.fullmatch(self.model)
                or not isinstance(self.contract, str) or not 1 <= len(self.contract) <= 256
                or not callable(self.evaluate)):
            raise EngineError("invalid_profile")

    @property
    def fingerprint(self):
        # This is a host-declared contract, not authenticated immutable weights.
        return digest(canonical_bytes(["engine-lab-v1", self.model, self.contract]).decode())


class Engine:
    def __init__(self, profiles, *, enabled=False, reuse=True, max_calls=128,
                 max_questions=512, max_request_bytes=1048576):
        if type(enabled) is not bool or type(reuse) is not bool or not isinstance(profiles, dict) or not 1 <= len(profiles) <= 4:
            raise EngineError("invalid_configuration")
        for value, ceiling in ((max_calls, 512), (max_questions, 2048), (max_request_bytes, 1048576)):
            if type(value) is not int or not 0 <= value <= ceiling:
                raise EngineError("invalid_configuration")
        self.enabled = enabled
        self.reuse = reuse
        self._stages = 0
        self._profiles = {}
        for name, profile in profiles.items():
            self.set_profile(name, profile)
        self.max_calls, self.max_questions = max_calls, max_questions
        self.max_request_bytes = max_request_bytes
        self._cache = {}
        self._scope = uuid.uuid4().hex
        self._bindings = {}
        self._stopped = False
        self.stats = dict(backend_calls=0, questions=0, request_bytes=0,
                          response_bytes=0, cache_hits=0, completed_calls=0)

    def set_profile(self, name, profile):
        """Host-only explicit revision change. Old raw evidence stays separate."""
        if not isinstance(name, str) or not NAME.fullmatch(name) or not isinstance(profile, Profile):
            raise EngineError("invalid_profile")
        self._profiles[name] = profile

    def contracts(self):
        return {name: profile.fingerprint for name, profile in self._profiles.items()}

    def snapshot(self):
        return clone({"stats": self.stats, "stopped": self._stopped,
                      "cached_observations": list(self._cache.values())})

    def trusted_binding(self, ticket):
        """Host-owned immutable stage evidence, not a hash supplied by the caller."""
        if not isinstance(ticket, str) or ticket not in self._bindings:
            raise EngineError("unregistered_stage")
        return strict_json_loads(self._bindings[ticket])

    def _prepare(self, text):
        if not isinstance(text, str) or len(text.encode("utf-8")) > MAX_MANIFEST_BYTES:
            raise EngineError("manifest_size")
        manifest = strict_json_loads(text)
        if (not isinstance(manifest, dict)
                or set(manifest) != {"version", "session", "generation", "source_sha256", "contracts", "jobs"}
                or type(manifest["version"]) is not int or manifest["version"] != 1
                or not isinstance(manifest["session"], str) or not NAME.fullmatch(manifest["session"])
                or type(manifest["generation"]) is not int or not 1 <= manifest["generation"] <= 128
                or not isinstance(manifest["source_sha256"], str) or not HEX.fullmatch(manifest["source_sha256"])
                or manifest["contracts"] != self.contracts()
                or not isinstance(manifest["jobs"], list) or len(manifest["jobs"]) > MAX_JOBS):
            raise EngineError("manifest_shape_or_contract")
        prepared, seen = [], set()
        for job in manifest["jobs"]:
            if (not isinstance(job, dict) or set(job) != {"id", "request_json"}
                    or not isinstance(job["id"], str) or not NAME.fullmatch(job["id"])
                    or job["id"] in seen or not isinstance(job["request_json"], str)
                    or len(job["request_json"].encode("utf-8")) > MAX_REQUEST_BYTES):
                raise EngineError("invalid_or_duplicate_job")
            seen.add(job["id"])
            request = strict_json_loads(job["request_json"])
            if (not isinstance(request, dict) or set(request) != {"profile", "state", "questions"}
                    or not isinstance(request["profile"], str) or request["profile"] not in self._profiles
                    or not isinstance(request["state"], (str, dict, list)) or not request["state"]):
                raise EngineError("invalid_request")
            validate_questions(request["questions"], 8)
            profile = self._profiles[request["profile"]]
            key = digest(canonical_bytes([profile.fingerprint, job["request_json"]]).decode())
            if not self.reuse:
                key = digest(canonical_bytes([key, self._stages, job["id"]]).decode())
            prepared.append((job, request, profile, key))
        missing = {}
        for job, request, profile, key in prepared:
            if key not in self._cache:
                missing[key] = (job, request)
        if (self.stats["backend_calls"] + len(missing) > self.max_calls
                or self.stats["questions"] + sum(len(r["questions"]) for _, r in missing.values()) > self.max_questions
                or self.stats["request_bytes"] + sum(len(j["request_json"].encode()) for j, _ in missing.values()) > self.max_request_bytes):
            raise EngineError("preflight_budget")
        return manifest, prepared

    def judge_many(self, text):
        if not self.enabled:
            raise EngineError("engine_disabled")
        if self._stopped:
            raise EngineError("engine_stopped")
        rows = []
        try:
            self._stages += 1
            manifest, prepared = self._prepare(text)
            for job, request, profile, key in prepared:
                cached = key in self._cache
                if cached:
                    self.stats["cache_hits"] += 1
                else:
                    self.stats["backend_calls"] += 1
                    self.stats["questions"] += len(request["questions"])
                    self.stats["request_bytes"] += len(job["request_json"].encode())
                    # A backend cannot mutate the frozen request used for validation.
                    body = profile.evaluate(clone(request["state"]), clone(request["questions"]))
                    raw = canonical_bytes(body)
                    if len(raw) > MAX_RESPONSE_BYTES:
                        raise EngineError("response_size")
                    self.stats["response_bytes"] += len(raw)
                    body = strict_json_loads(raw)
                    validate_response(body, request["questions"], profile.model)
                    self._cache[key] = raw.decode("utf-8")
                    self.stats["completed_calls"] += 1
                rows.append({"id": job["id"], "profile": request["profile"],
                             "request_sha256": digest(job["request_json"]),
                             "contract_sha256": profile.fingerprint,
                             "response_json": self._cache[key], "cached": cached})
            ticket = digest(canonical_bytes([self._scope, self._stages, digest(text)]).decode())
            binding = {"stage_ticket": ticket, "session": manifest["session"],
                       "generation": manifest["generation"], "source_sha256": manifest["source_sha256"],
                       "manifest_sha256": digest(text), "observations": {
                           row["id"]: {"request_sha256": row["request_sha256"],
                                       "response_sha256": digest(row["response_json"]),
                                       "contract_sha256": row["contract_sha256"]}
                           for row in rows}}
            self._bindings[ticket] = canonical_bytes(binding)
            return clone({"version": 1, "complete": True, "stage_ticket": ticket, "session": manifest["session"],
                          "generation": manifest["generation"], "source_sha256": manifest["source_sha256"],
                          "manifest_sha256": digest(text), "rows": rows, "stats": self.stats})
        except BaseException as exc:
            self._stopped = True
            if not isinstance(exc, Exception):
                raise
            code = str(exc) if isinstance(exc, (EngineError, AdapterError)) else "backend_failure"
            raise EngineError(code, partial=rows) from None
