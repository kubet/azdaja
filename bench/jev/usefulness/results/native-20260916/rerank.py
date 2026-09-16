request = json.loads(judgment_payload)
failed = None
try:
    observation = judge_many(request["state"], request["questions"])
except Exception as problem:
    failed = str(problem)
if failed is not None:
    FINAL({"failed":failed,"stats":judge_stats()})
else:
    cached = judge_many(request["state"], request["questions"])
    assert observation["answers"] == cached["answers"]
    assert cached["_azdaja"]["cache_hit"]
    FINAL({"observation":observation,"cached":cached,"stats":judge_stats()})
