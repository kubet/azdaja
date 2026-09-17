
request = json.loads(judge_payload)
failed = None
try:
    observation = judge_many(request["state"], request["questions"])
except Exception as error:
    failed = str(error)
if failed is not None:
    FINAL({"failed":failed,"stats":judge_stats()})
else:
    cached = judge_many(request["state"], request["questions"])
    assert cached["answers"] == observation["answers"]
    assert cached["_azdaja"]["cache_hit"]
    retained_observations[request["name"]] = observation
    FINAL({"observation":observation,"cached":cached,"stats":judge_stats()})
