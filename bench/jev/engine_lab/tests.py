"""Oracle-only controls. A green test can mean a proposed optimization was false."""
import os
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

from ..adapter import canonical_bytes, strict_json_loads
from .kernel import Engine, EngineError, Profile, clone, digest
from .monty import Session
from . import scenarios as s

OBSERVATIONS = {}


def manifest(engine, requests):
    return canonical_bytes({"version": 1, "session": "unit-session", "generation": 1,
        "source_sha256": "a" * 64, "contracts": engine.contracts(),
        "jobs": [{"id": str(i), "request_json": canonical_bytes(req).decode()}
                 for i, req in enumerate(requests)]}).decode()


def request(state=None, questions=None, profile="fast"):
    return {"profile": profile, "state": state or {"text": "synthetic"},
            "questions": clone(questions or s.QUESTION)}


class OfflineTests(unittest.TestCase):
    def setUp(self):
        self.binary = Path(os.environ.get("AZDAJA_BINARY", "target/debug/azdaja")).resolve(strict=True)
        self.scratch = Path(os.environ.get("JCODE_SCRATCH_DIR", str(Path.home() / ".jcode/scratch")))
        forbidden = []
        def deny(*_args, **_kwargs):
            forbidden.append("network")
            raise AssertionError("network forbidden")
        self.addCleanup(lambda: self.assertEqual(forbidden, [], "forbidden operation was attempted"))
        original_popen = subprocess.Popen
        def guarded(argv, *args, **kwargs):
            if (not isinstance(argv, list) or Path(argv[0]) != self.binary
                    or argv[1] not in ("start", "load", "exec", "final", "kill")):
                forbidden.append("child")
                raise AssertionError("unapproved child process")
            return original_popen(argv, *args, **kwargs)
        for guard in (
            patch.dict(os.environ, {"PATH": os.defpath}, clear=True),
            patch("socket.create_connection", side_effect=deny),
            patch("socket.socket.connect", side_effect=deny),
            patch("http.client.HTTPSConnection", side_effect=deny),
            patch("subprocess.Popen", side_effect=guarded),
        ):
            guard.start()
            self.addCleanup(guard.stop)

    def session(self, engine, source=None):
        return Session(self.binary, self.scratch, s.records(1) if source is None else source, engine.contracts())


class KernelTests(OfflineTests):
    def profile(self, seen, model="oracle-v1", contract="unit-v1"):
        def evaluate(state, questions):
            seen.append((state, questions))
            return s.body({qid: s.choice("yes") for qid in questions}, model)
        return Profile(model, contract, evaluate)

    def test_default_disabled_never_enters_backend(self):
        seen = []
        engine = Engine({"fast": self.profile(seen)})
        with self.assertRaisesRegex(EngineError, "^engine_disabled$"):
            engine.judge_many(manifest(engine, [request()]))
        self.assertEqual(seen, [])

    def test_whole_stage_budget_preflight_never_partly_executes(self):
        for limits in ({"max_calls": 0}, {"max_questions": 0}, {"max_request_bytes": 1}):
            seen = []
            engine = Engine({"fast": self.profile(seen)}, enabled=True, **limits)
            with self.subTest(limits=limits), self.assertRaisesRegex(EngineError, "^preflight_budget$"):
                engine.judge_many(manifest(engine, [request()]))
            self.assertEqual(seen, [])

    def test_three_primitives_are_data_and_questions_are_not_requests(self):
        questions = clone(s.QUESTION)
        questions["present"] = {"type": "noul", "instructions": "Is the condition stated?"}
        questions["degree"] = {"type": "score", "instructions": "Rate the stated degree.", "criteria": ["absent", "present"]}
        answers = {"decision": s.choice("yes"), "present": {"type": "noul", "noul": 0.4},
                   "degree": {"type": "score", "score": 0.75, "probabilities": {"0": 0.25, "1": 0.75},
                              "legend": {"0": "absent", "1": "present"}, "confidence": 0.6}}
        engine = Engine({"fast": Profile("oracle-v1", "three-types", lambda *_: s.body(answers))}, enabled=True)
        result = engine.judge_many(manifest(engine, [request(questions=questions)]))
        self.assertEqual(strict_json_loads(result["rows"][0]["response_json"])["answers"], answers)
        self.assertEqual(result["stats"]["questions"], 3)
        self.assertEqual(result["stats"]["backend_calls"], 1)
        with self.session(engine, [{"text": "synthetic"}]) as session:
            session.load("request_raw", canonical_bytes(request(questions=questions)).decode())
            stage = session.plan('jobs = [{"id": "all", "request_json": request_raw}]')
            session.bind(engine, engine.judge_many(stage))
            self.assertEqual(session.value('FINAL(bound["all"])'), answers)

    def test_profile_model_identity_supports_versioned_provider_names(self):
        seen = []
        # A synthetic model identity, not an assertion of account availability.
        engine = Engine({"fast": self.profile(seen, model="vendor/model.1")}, enabled=True)
        output = engine.judge_many(manifest(engine, [request()]))
        self.assertEqual(strict_json_loads(output["rows"][0]["response_json"])["model"], "vendor/model.1")

    def test_malformed_answers_cannot_become_observations(self):
        mutations = [
            (lambda b: b["answers"].clear(), "answer_coverage_mismatch"),
            (lambda b: b["answers"].update(extra=s.choice("yes")), "answer_coverage_mismatch"),
            (lambda b: b["answers"]["decision"]["probabilities"].update(yes=1.5), "invalid_probability"),
            (lambda b: b["answers"]["decision"].update(confidence=True), "invalid_probability"),
            (lambda b: b.update(model="different"), "response_model_mismatch"),
            (lambda b: b["answers"]["decision"].update(choice="no"), "choice_not_argmax"),
        ]
        for mutate, error in mutations:
            body = s.body({"decision": s.choice("yes")})
            mutate(body)
            engine = Engine({"fast": Profile("oracle-v1", "bad-response", lambda *_: body)}, enabled=True)
            with self.subTest(error=error), self.assertRaisesRegex(EngineError, "^" + error + "$"):
                engine.judge_many(manifest(engine, [request()]))
            self.assertEqual(engine.snapshot()["cached_observations"], [])

    def test_reuse_preserves_occurrences_and_each_identity_mutation_misses(self):
        seen = []
        engine = Engine({"fast": self.profile(seen)}, enabled=True)
        req = request(state={"nested": {"text": "one"}})
        frozen = manifest(engine, [req, req])
        first = engine.judge_many(frozen)
        self.assertEqual(len(first["rows"]), 2)
        self.assertEqual([r["cached"] for r in first["rows"]], [False, True])
        first["rows"][0]["response_json"] = "mutated by caller"
        repeated = engine.judge_many(frozen)
        self.assertEqual(len(seen), 1)
        self.assertNotEqual(repeated["rows"][0]["response_json"], "mutated by caller")
        req["state"]["nested"]["text"] = "two"
        engine.judge_many(manifest(engine, [req]))
        req["questions"]["decision"]["instructions"] += " Use only this record."
        engine.judge_many(manifest(engine, [req]))
        criteria = req["questions"]["decision"]["criteria"]
        req["questions"]["decision"]["criteria"] = dict(reversed(list(criteria.items())))
        engine.judge_many(manifest(engine, [req]))
        engine.set_profile("fast", self.profile(seen, contract="unit-v2"))
        engine.judge_many(manifest(engine, [req]))
        engine.set_profile("fast", self.profile(seen, model="oracle-v2", contract="unit-v2"))
        engine.judge_many(manifest(engine, [req]))
        self.assertEqual(len(seen), 6)

    def test_backend_argument_mutation_does_not_rewrite_frozen_request(self):
        def evaluate(state, questions):
            state.clear()
            questions.clear()
            return s.body({"decision": s.choice("yes")})
        engine = Engine({"fast": Profile("oracle-v1", "mutating-backend", evaluate)}, enabled=True)
        text = manifest(engine, [request()])
        result = engine.judge_many(text)
        self.assertEqual(result["rows"][0]["request_sha256"], digest(strict_json_loads(text)["jobs"][0]["request_json"]))

    def test_partial_failure_keeps_prior_observation_but_never_complete_stage(self):
        calls = []
        def evaluate(state, questions):
            calls.append(state)
            if len(calls) == 2:
                raise RuntimeError("untrusted provider message")
            return s.body({"decision": s.choice("yes")})
        engine = Engine({"fast": Profile("oracle-v1", "partial-failure", evaluate)}, enabled=True)
        with self.assertRaisesRegex(EngineError, "^backend_failure$") as caught:
            engine.judge_many(manifest(engine, [request({"n": 1}), request({"n": 2})]))
        self.assertEqual(len(caught.exception.partial), 1)
        self.assertEqual(len(engine.snapshot()["cached_observations"]), 1)
        with self.assertRaisesRegex(EngineError, "^engine_stopped$"):
            engine.judge_many(manifest(engine, [request()]))
        self.assertEqual(len(calls), 2)

    def test_manifest_is_data_not_permission_to_expand_capabilities(self):
        mutations = [
            lambda m: m.update(command="run something"),
            lambda m: m.update(contracts={"fast": "0" * 64}),
            lambda m: m["jobs"].append(clone(m["jobs"][0])),
            lambda m: m["jobs"][0].update(request_json=" " * 32769),
            lambda m: m["jobs"][0].update(request_json=canonical_bytes(request(profile="unregistered")).decode()),
            lambda m: m["jobs"][0].update(request_json=canonical_bytes(request(questions={"q": {"type": "generate", "instructions": "text"}})).decode()),
        ]
        for mutate in mutations:
            seen = []
            engine = Engine({"fast": self.profile(seen)}, enabled=True)
            value = strict_json_loads(manifest(engine, [request()]))
            mutate(value)
            with self.assertRaises(EngineError):
                engine.judge_many(canonical_bytes(value).decode())
            self.assertEqual(seen, [])


class MechanismTests(OfflineTests):
    def test_factorable_query_matches_independent_pairs_and_strong_python(self):
        rows = s.records()
        reference = s.direct_pair_ledger(rows)
        python_features, python_calls = {}, 0
        oracle = s.unary_profile()
        for row in rows:
            if row["id"] not in python_features:
                python_calls += 1
                a = oracle.evaluate(row, s.QUESTION)["answers"]["decision"]
                python_features[row["id"]] = a["choice"] == "yes"
        self.assertEqual(s.python_factor_ledger(rows, python_features), reference)
        observed = {}
        for reuse in (False, True):
            engine = Engine({"fast": s.unary_profile()}, enabled=True, reuse=reuse)
            with self.session(engine, rows) as session:
                s.load_question(session)
                frozen = session.plan(s.PLAN_UNARY)
                result = engine.judge_many(frozen)
                result["rows"].reverse()  # Re-entry must be ID-based, not positional.
                self.assertEqual(session.bind(engine, result)["bound"], len(rows))
                output = s.reduce(session)
                ledger = session.value("FINAL(ledger)")
                self.assertEqual(ledger, reference)
                self.assertTrue(output["complete"])
                self.assertEqual(output["pair_count"], 2556)
                self.assertEqual(len(output["edges"]), 336)
                summary = session.value('FINAL({"pairs": len(ledger), "positive": len(edges)})')
                self.assertLess(len(canonical_bytes(summary)), 128)
                self.assertGreater(len(canonical_bytes(ledger)), 20000)
                if reuse:
                    before = clone(engine.stats)
                    stricter = s.reduce(session, 0.99)
                    self.assertFalse(stricter["complete"])
                    self.assertEqual(engine.stats, before)
                    # A second view is another generation, but not new evidence.
                    session.bind(engine, engine.judge_many(session.plan(s.PLAN_UNARY)))
                    self.assertEqual(s.reduce(session)["edges"], output["edges"])
                    self.assertEqual(engine.stats["backend_calls"], 16)
                observed[str(reuse)] = clone(engine.stats)
        self.assertEqual(observed["False"]["questions"], 72)
        self.assertEqual(observed["True"]["questions"], python_calls)
        OBSERVATIONS["M1_M4_M6"] = {"occurrences": 72, "unique_source_records": 16,
            "pair_universe": len(reference), "positive_pairs": 336,
            "matched_python_semantic_questions": python_calls, "same_plan_python_equal": True,
            "direct_pair_oracle_evaluations": len(reference), "cache_off": observed["False"],
            "cache_on_after_second_view": observed["True"], "full_ledger_bytes": len(canonical_bytes(reference)),
            "root_summary_bytes": len(canonical_bytes(summary)), "automatic_plan_generation": False}

    def test_high_confidence_wrong_feature_amplifies_and_is_not_repaired(self):
        rows = s.records()
        engine = Engine({"fast": s.unary_profile(flipped="r00")}, enabled=True)
        with self.session(engine, rows) as session:
            s.load_question(session)
            session.bind(engine, engine.judge_many(session.plan(s.PLAN_UNARY)))
            output = s.reduce(session)
            ledger = session.value("FINAL(ledger)")
        errors = sum(a != b for a, b in zip(ledger, s.direct_pair_ledger(rows)))
        self.assertEqual(errors, 96)
        self.assertTrue(output["complete"])
        self.assertEqual(output["unknown"], [])
        OBSERVATIONS["wrong_feature_falsifier"] = {"unique_wrong_features": 1,
            "wrong_pair_decisions": errors, "structurally_complete": True,
            "claim_that_exact_join_repairs_semantics": "falsified"}

    def test_collision_forces_direct_relation_requests_not_unary_reduction(self):
        cases = s.FIXTURES["relation_cases"]
        self.assertEqual(cases[0]["unary_features"], cases[1]["unary_features"])
        self.assertNotEqual(cases[0]["gold_positive_pairs"], cases[1]["gold_positive_pairs"])
        outputs = []
        engine = Engine({"pair": s.relation_profile()}, enabled=True)
        for case in cases:
            query = {k: case[k] for k in ("name", "evidence")}
            query["supplied_unary_factorization_contract"] = False
            with self.session(engine, query) as session:
                session.execute("query = records\n")
                session.bind(engine, engine.judge_many(session.plan(s.PLAN_RELATION)))
                positive = session.value('pairs = []\nfor job in manifest["jobs"]:\n    if bound[job["id"]]["relation"]["noul"] == 1.0:\n        pairs.append(json.loads(job["request_json"])["state"]["pair"])\nFINAL(pairs)')
                self.assertEqual(positive, case["gold_positive_pairs"])
                outputs.append(positive)
        self.assertEqual(engine.stats["questions"], 6)
        self.assertNotEqual(outputs[0], outputs[1])
        OBSERVATIONS["M2"] = {"same_chosen_unary_features": True, "pair_outputs_differ": True,
            "sufficiency_of_these_chosen_unary_features": "falsified", "fallback": "direct_pair_requests",
            "fallback_questions": engine.stats["questions"], "automatic_collision_discovery": False}

    def test_residual_escalation_preserves_unknown_and_resolves_only_eligible_rows(self):
        engine = Engine({"fast": s.unary_profile(residual=True),
                         "expert": s.unary_profile(residual=True, expert=True)}, enabled=True)
        rows = s.records(1)
        with self.session(engine, rows) as session:
            s.load_question(session)
            session.bind(engine, engine.judge_many(session.plan(s.PLAN_UNARY)))
            before = s.reduce(session)
            residual_manifest = session.plan(s.PLAN_RESIDUAL)
            ids = [job["id"] for job in strict_json_loads(residual_manifest)["jobs"]]
            self.assertEqual(ids, ["0", "8", "16"])
            session.bind(engine, engine.judge_many(residual_manifest))
            session.execute(s.MERGE_RESIDUAL)
            after = s.reduce(session)
            ledger = session.value("FINAL(ledger)")
            for observed, truth in zip(ledger, s.direct_pair_ledger(rows)):
                if observed[2] is not None:
                    self.assertEqual(observed, truth)
        self.assertEqual(len(before["unknown"]), 9)
        self.assertEqual(len(after["unknown"]), 3)
        self.assertFalse(after["complete"])
        self.assertEqual(engine.stats["backend_calls"], 18)
        self.assertEqual(before["states"][0], "abstained")
        self.assertEqual(before["states"][8], "semantic_unknown")
        OBSERVATIONS["M3"] = {"residual_occurrence_ids": ids, "additional_unique_questions": 2,
            "unknown_pairs_before": 9, "unknown_pairs_after": 3, "complete": False,
            "real_generative_llm_called": False}

    def test_budget_stop_does_not_convert_unjudged_residuals_to_false(self):
        engine = Engine({"fast": s.unary_profile(residual=True),
                         "expert": s.unary_profile(residual=True, expert=True)}, enabled=True, max_calls=16)
        with self.session(engine) as session:
            s.load_question(session)
            session.bind(engine, engine.judge_many(session.plan(s.PLAN_UNARY)))
            before = s.reduce(session)
            with self.assertRaisesRegex(EngineError, "^preflight_budget$"):
                engine.judge_many(session.plan(s.PLAN_RESIDUAL))
            self.assertEqual(s.reduce(session), before)
        self.assertEqual(engine.stats["backend_calls"], 16)
        self.assertEqual(len(before["unknown"]), 9)

    def test_reentry_rejects_misbinding_without_falling_back_to_old_variables(self):
        mutations = [
            (lambda x: x.update(session="another-session"), "session mismatch"),
            (lambda x: x.update(generation=99), "generation mismatch"),
            (lambda x: x.update(source_sha256="0" * 64), "source mismatch"),
            (lambda x: x.update(manifest_sha256="0" * 64), "manifest mismatch"),
            (lambda x: x["rows"].pop(), "missing response"),
            (lambda x: x["rows"].append(clone(x["rows"][0])), "unexpected or duplicate response"),
            (lambda x: x["rows"][0].update(id="extra"), "unexpected or duplicate response"),
            (lambda x: x["rows"][0].update(request_sha256="0" * 64), "request mismatch"),
            (lambda x: x["rows"][0].update(contract_sha256="0" * 64), "contract mismatch"),
        ]
        for mutate, message in mutations:
            engine = Engine({"fast": s.unary_profile()}, enabled=True)
            with self.subTest(message=message), self.session(engine, s.records(1)[:2]) as session:
                s.load_question(session)
                result = engine.judge_many(session.plan(s.PLAN_UNARY))
                mutate(result)
                with self.assertRaisesRegex(ValueError, message):
                    session.bind(engine, result)
                with self.assertRaisesRegex(ValueError, "session stopped"):
                    session.value("FINAL(bound)")

    def test_previous_generation_and_changed_source_are_rejected_in_evaluator(self):
        for changed_source in (False, True):
            engine = Engine({"fast": s.unary_profile()}, enabled=True)
            with self.subTest(source=changed_source), self.session(engine, s.records(1)[:2]) as session:
                s.load_question(session)
                first = engine.judge_many(session.plan(s.PLAN_UNARY))
                session.bind(engine, first)
                if changed_source:
                    session.load("source", canonical_bytes(s.records(1)[:3]).decode())
                    error = "source mismatch"
                else:
                    session.plan(s.PLAN_UNARY)
                    error = "generation mismatch"
                with self.assertRaisesRegex(ValueError, error):
                    session.bind(engine, first)

    def test_malformed_body_and_valid_body_swap_cannot_cross_reentry(self):
        for mode in ("invalid_probability_and_model", "valid_body_swap"):
            engine = Engine({"fast": s.unary_profile()}, enabled=True)
            with self.subTest(mode=mode), self.session(engine, s.records(1)[:3]) as session:
                s.load_question(session)
                result = engine.judge_many(session.plan(s.PLAN_UNARY))
                if mode == "valid_body_swap":
                    a, b = result["rows"][0], result["rows"][2]
                    a["response_json"], b["response_json"] = b["response_json"], a["response_json"]
                else:
                    body = strict_json_loads(result["rows"][0]["response_json"])
                    body["model"] = "wrong-model"
                    body["answers"]["decision"]["probabilities"]["yes"] = 1.5
                    result["rows"][0]["response_json"] = canonical_bytes(body).decode()
                # Rehashing a mutable view or binding copy cannot rewrite the
                # engine-owned immutable per-request response association.
                fake = engine.trusted_binding(result["stage_ticket"])
                fake["observations"]["0"]["response_sha256"] = digest(result["rows"][0]["response_json"])
                result["rows"][0]["response_sha256"] = fake["observations"]["0"]["response_sha256"]
                with self.assertRaisesRegex(ValueError, "response observation mismatch"):
                    session.bind(engine, result)
                with self.assertRaisesRegex(ValueError, "session stopped"):
                    session.value("FINAL(bound)")

    def test_process_exception_poisoning_prevents_old_stage_reuse(self):
        engine = Engine({"fast": s.unary_profile()}, enabled=True)
        with self.session(engine, s.records(1)[:3]) as session:
            s.load_question(session)
            result = engine.judge_many(session.plan(s.PLAN_UNARY))
            session.bind(engine, result)
            with patch("bench.jev.engine_lab.monty._run", side_effect=ValueError("offline evaluator process failed")):
                with self.assertRaisesRegex(ValueError, "offline evaluator process failed"):
                    session.bind(engine, result)
            self.assertTrue(session.stopped)
            with self.assertRaisesRegex(ValueError, "session stopped"):
                session.value("FINAL(bound)")

    def test_oversized_reentry_poisoning_prevents_old_stage_reuse(self):
        engine = Engine({"fast": s.unary_profile()}, enabled=True)
        with self.session(engine, s.records(1)[:3]) as session:
            s.load_question(session)
            result = engine.judge_many(session.plan(s.PLAN_UNARY))
            session.bind(engine, result)
            result["rows"][0]["response_json"] = " " * 262145
            with self.assertRaisesRegex(ValueError, "invalid load"):
                session.bind(engine, result)
            self.assertTrue(session.stopped)
            with self.assertRaisesRegex(ValueError, "session stopped"):
                session.value("FINAL(bound)")

    def test_ticket_from_different_engine_is_not_local_observation_authority(self):
        engine = Engine({"fast": s.unary_profile()}, enabled=True)
        other = Engine({"fast": s.unary_profile()}, enabled=True)
        with self.session(engine, s.records(1)[:3]) as session:
            s.load_question(session)
            result = other.judge_many(session.plan(s.PLAN_UNARY))
            with self.assertRaisesRegex(EngineError, "^unregistered_stage$"):
                session.bind(engine, result)
            self.assertTrue(session.stopped)
