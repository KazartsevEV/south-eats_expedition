#!/usr/bin/env python3
import json
from pathlib import Path

p=Path("data/source/laos.json")
d=json.loads(p.read_text(encoding="utf-8"))

def find(n):
    if isinstance(n,dict):
        if n.get("name")=="Tham Chang Cave": return n
        for v in n.values():
            x=find(v)
            if x is not None:return x
    elif isinstance(n,list):
        for v in n:
            x=find(v)
            if x is not None:return x
    return None

def repl(v):
    if isinstance(v,dict):
        return {k:repl(x) for k,x in v.items()}
    if isinstance(v,list):
        return [repl(x) for x in v]
    if v=="src:9799177acb170c":
        return "src_000283"
    return v

o=find(d)
if o is None: raise SystemExit("Tham Chang Cave not found")
new=repl(o)
o.clear(); o.update(new)
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("replaced Tham Chang Tourism Laos legacy refs with src_000283")
