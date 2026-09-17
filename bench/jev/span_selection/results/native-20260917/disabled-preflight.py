retained_results = {}
retained_observations = {}
failed = None
try:
    judge_many("probe", {"p":{"type":"noul","instructions":"probe"}})
except Exception as error:
    failed = str(error)
FINAL({"failed":failed,"stats":judge_stats()})
