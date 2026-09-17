
p = json.loads(projection_payload)
rows = []
for task in p["pack"]["tasks"]:
    source = task["source"]
    choice = p["selections"][task["id"]]
    row = {"id":task["id"],"choice":choice,"status":choice if choice in p["sentinels"] else "selected","value":None,"source_sha256":source["sha256"],"path":source["path"],"commit":source["commit"],"start":None,"end":None,"byte_start":None,"byte_end":None}
    found = False
    for candidate in task["candidates"]:
        if candidate["id"] == choice:
            assert not found
            found = True
            value = source["text"][candidate["start"]:candidate["end"]]
            assert value == candidate["text"]
            row["value"] = value
            for field in ["start","end","byte_start","byte_end"]:
                row[field] = candidate[field]
    assert found or choice in p["sentinels"]
    rows.append(row)
projection_result = {"rows":rows,"source_pool":p["pack"],"selections":p["selections"]}
retained_results[p["name"]] = projection_result
FINAL(projection_result)
