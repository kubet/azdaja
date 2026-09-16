"""Explicit synthetic oracles and handwritten programs, never learned planners."""
from pathlib import Path

from ..adapter import canonical_bytes, strict_json_loads
from .kernel import Profile, clone

HERE = Path(__file__).resolve().parent
FIXTURES = strict_json_loads((HERE / "fixtures.json").read_bytes())
QUESTION = {"decision": {"type": "choice",
    "instructions": "Does this record state that an attempted operation was rejected by an authorization policy? Distinguish authentication, parsing, networking and user cancellation from authorization rejection.",
    "criteria": {"yes": "The record states an authorization-policy rejection.",
                 "no": "The record states another outcome, not an authorization-policy rejection.",
                 "unknown": "The supplied record does not establish either answer."}}}


def body(answers, model="oracle-v1"):
    return {"model": model, "answers": answers,
            "usage": {"input_tokens": None, "output_tokens": None}}


def choice(label, *, uncertain=False):
    probs = {name: (0.98 if name == label else 0.01) for name in ("yes", "no", "unknown")}
    if uncertain:
        probs = {name: (0.5 if name == label else 0.25) for name in probs}
    return {"type": "choice", "choice": label, "probabilities": probs,
            "confidence": 0.2 if uncertain else 0.95}


def records(repetitions=4):
    by_id = {r["id"]: r for r in FIXTURES["records"]}
    return clone([by_id[rid] for rid in FIXTURES["base_occurrence_ids"]] * repetitions)


def unary_profile(*, residual=False, expert=False, flipped=None):
    policy = FIXTURES["residual_policy"]
    def evaluate(state, questions):
        rid = state["id"]
        label = "yes" if FIXTURES["gold_features"][rid] else "no"
        uncertain = residual and not expert and rid in policy["fast_abstained_ids"]
        if residual and rid in policy["expert_semantic_unknown_ids" if expert else "fast_semantic_unknown_ids"]:
            label = "unknown"
        if rid == flipped:
            label = "no" if label == "yes" else "yes"
        return body({qid: choice(label, uncertain=uncertain) for qid in questions})
    return Profile("oracle-v1", f"synthetic-unary-v1-residual-{residual}-expert-{expert}-flip-{flipped}", evaluate)


def direct_pair_ledger(rows):
    """Independent literal pair truth. Does not read features or combine fields."""
    positives = {frozenset(pair) for pair in FIXTURES["gold_positive_pairs"]}
    return [[i, j, frozenset((rows[i]["id"], rows[j]["id"])) in positives]
            for i in range(len(rows)) for j in range(i + 1, len(rows))]


def python_factor_ledger(rows, features):
    """Competent plain-Python same-plan baseline, not the direct-pair reference."""
    values = []
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            exact = rows[i]["day"] == rows[j]["day"] and rows[i]["tenant"] != rows[j]["tenant"]
            values.append([i, j, bool(exact and features[rows[i]["id"]] and features[rows[j]["id"]])])
    return values


PLAN_UNARY = '''questions = json.loads(question_raw)
jobs = []
for i in range(len(records)):
    request = {"profile": "fast", "state": records[i], "questions": questions}
    jobs.append({"id": str(i), "request_json": json.dumps(request)})
'''

REDUCE = '''states = []
values = []
for i in range(len(records)):
    a = bound[str(i)]["decision"]
    value = None
    status = "abstained"
    if a["choice"] == "unknown":
        status = "semantic_unknown"
    elif a["probabilities"][a["choice"]] >= threshold and a["confidence"] >= 0.9:
        value = a["choice"] == "yes"
        status = "accepted"
    values.append(value)
    states.append(status)
ledger = []
edges = []
unknown = []
for i in range(len(records)):
    for j in range(i + 1, len(records)):
        exact = records[i]["day"] == records[j]["day"] and records[i]["tenant"] != records[j]["tenant"]
        value = None
        if not exact or values[i] == False or values[j] == False:
            value = False
        elif values[i] == True and values[j] == True:
            value = True
        ledger.append([i, j, value])
        if value == True:
            edges.append([i,j])
        elif value == None:
            unknown.append([i,j])
FINAL({"edges": edges, "unknown": unknown, "pair_count": len(ledger),
       "ledger_sha256": sha256(json.dumps(ledger)), "states": states,
       "complete": len(unknown) == 0})
'''

PLAN_RESIDUAL = '''first_bound = bound
jobs = []
residual_ids = []
for i in range(len(records)):
    if states[i] != "accepted":
        residual_ids.append(str(i))
        request = {"profile": "expert", "state": records[i], "questions": questions}
        jobs.append({"id": str(i), "request_json": json.dumps(request)})
'''

MERGE_RESIDUAL = '''for rid in bound:
    assert rid in residual_ids, "unexpected residual"
    first_bound[rid] = bound[rid]
bound = first_bound
'''


def load_question(session):
    session.load("question_raw", canonical_bytes(QUESTION).decode())


def reduce(session, threshold=0.9):
    return session.value(f"threshold = {threshold!r}\n" + REDUCE)


def relation_profile():
    lookup = {case["name"]: {tuple(p) for p in case["gold_positive_pairs"]}
              for case in FIXTURES["relation_cases"]}
    def evaluate(state, questions):
        yes = tuple(state["pair"]) in lookup[state["case"]]
        return body({qid: {"type": "noul", "noul": 1.0 if yes else 0.0} for qid in questions})
    return Profile("oracle-v1", "synthetic-direct-relation-v1", evaluate)


PLAN_RELATION = '''assert not query["supplied_unary_factorization_contract"], "this branch is direct-only"
jobs = []
names = ["a", "b", "c"]
for i in range(3):
    for j in range(i + 1, 3):
        state = {"case": query["name"], "evidence": query["evidence"], "pair": [names[i], names[j]]}
        q = {"relation": {"type": "noul", "instructions": "Does the first policy in pair explicitly replace the second policy, according to evidence?"}}
        request = {"profile": "pair", "state": state, "questions": q}
        jobs.append({"id": str(i) + "_" + str(j), "request_json": json.dumps(request)})
'''
