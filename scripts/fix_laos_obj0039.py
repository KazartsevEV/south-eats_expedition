#!/usr/bin/env python3
import json
from pathlib import Path

p=Path("data/source/laos.json")
d=json.loads(p.read_text(encoding="utf-8"))

def find(node):
    if isinstance(node,dict):
        if node.get("name")=="Tad Saleuy Waterfall":
            return node
        for v in node.values():
            x=find(v)
            if x is not None:return x
    elif isinstance(node,list):
        for v in node:
            x=find(v)
            if x is not None:return x
    return None

o=find(d)
if o is None: raise SystemExit("object not found")
loc=o["traveler_card"]["location"]
loc["object_elevation"]["reference_type"]="characteristic"
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("fixed Tad Saleuy elevation reference_type")
