#!/usr/bin/env python3
import argparse,json,re,sys
p=argparse.ArgumentParser();p.add_argument("path");p.add_argument("--prime-jsonl",action="store_true");a=p.parse_args();text=open(a.path).read()
if a.prime_jsonl:
    final=""
    for line in text.splitlines():
        try:o=json.loads(line)
        except json.JSONDecodeError:continue
        if o.get("type")=="message_end" and o.get("message",{}).get("role")=="assistant":
            chunks=[c.get("text","") for c in o["message"].get("content",[]) if c.get("type")=="text"]
            if chunks:final="".join(chunks)
    text=final
gold={"INC-101":"credential expiry","INC-102":"network saturation","INC-103":"storage exhaustion","INC-104":"credential expiry","INC-105":"storage exhaustion","INC-106":"network saturation"}
got={}
for ident,cat in re.findall(r"(INC-10[1-6])\s*(?:->|→|:|=)\s*(credential expiry|network saturation|storage exhaustion)",text,re.I):got[ident]=cat.lower()
if got!=gold:print(json.dumps({"correct":False,"got":got,"gold":gold},indent=2));sys.exit(1)
print(json.dumps({"correct":True,"mapping":got},indent=2))
