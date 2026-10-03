#!/usr/bin/env python3
import json
from pathlib import Path
p=Path("data/source/laos.json")
d=json.loads(p.read_text(encoding="utf-8"))
def find(n):
    if isinstance(n,dict):
        if n.get("name")=="Tad Saleuy Waterfall": return n
        for v in n.values():
            x=find(v)
            if x is not None:return x
    elif isinstance(n,list):
        for v in n:
            x=find(v)
            if x is not None:return x
    return None
o=find(d)
if o is None: raise SystemExit("object not found")
o["traveler_card"]["media"]["drone"]["source_refs"]=["src:23a65d16d80264"]
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("fixed Tad Saleuy drone source ref")
