#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"data"/"source"/"laos.json"
REGISTRY=ROOT/"data"/"id-registry.json"

URLS={
 "https://commons.wikimedia.org/wiki/Category:Tham_Jang":"src_990507",
 "https://commons.wikimedia.org/wiki/File:View_from_the_Tham_Jang.jpg":"src_990508",
 "https://commons.wikimedia.org/wiki/File:Tham_Jang_2.jpg":"src_990509",
 "https://commons.wikimedia.org/wiki/File:Tham_Jang_Lagoon_1.jpg":"src_990510",
}

def key(url):
    return "src:"+hashlib.sha1(url.encode("utf-8")).hexdigest()[:14]

def find(node):
    if isinstance(node,dict):
        if node.get("name")=="Tham Chang Cave": return node
        for v in node.values():
            x=find(v)
            if x is not None:return x
    elif isinstance(node,list):
        for v in node:
            x=find(v)
            if x is not None:return x
    return None

data=json.loads(SOURCE.read_text(encoding="utf-8"))
obj=find(data)
if obj is None: raise SystemExit("Tham Chang Cave not found")

extra=[
 {
  "type":"other",
  "title":"Tham Jang — Wikimedia Commons category",
  "publisher":"Wikimedia Commons",
  "url":"https://commons.wikimedia.org/wiki/Category:Tham_Jang",
  "language":"en","published_at":None,"authority":"medium",
  "used_for":["geotagged cave identity","visual reconnaissance"],
  "accessed":"2026-10-03"
 },
 {
  "type":"other",
  "title":"View from the Tham Jang",
  "publisher":"Wikimedia Commons",
  "url":"https://commons.wikimedia.org/wiki/File:View_from_the_Tham_Jang.jpg",
  "language":"en","published_at":"2018-08-22","authority":"medium",
  "used_for":["cave-mouth viewpoint","valley visual reconnaissance"],
  "accessed":"2026-10-03","notes":"CC BY-SA 4.0; author Christophe95."
 },
 {
  "type":"other",
  "title":"Tham Jang 2",
  "publisher":"Wikimedia Commons",
  "url":"https://commons.wikimedia.org/wiki/File:Tham_Jang_2.jpg",
  "language":"en","published_at":"2018-08-22","authority":"medium",
  "used_for":["cave interior visual reconnaissance"],
  "accessed":"2026-10-03","notes":"CC BY-SA 4.0; author Christophe95."
 },
 {
  "type":"other",
  "title":"Tham Jang Lagoon 1",
  "publisher":"Wikimedia Commons",
  "url":"https://commons.wikimedia.org/wiki/File:Tham_Jang_Lagoon_1.jpg",
  "language":"en","published_at":"2018-08-22","authority":"medium",
  "used_for":["karst spring visual reconnaissance"],
  "accessed":"2026-10-03","notes":"CC BY-SA 4.0; author Christophe95."
 },
]
by={s.get("url"):s for s in (obj.get("sources") or []) if isinstance(s,dict) and s.get("url")}
for s in extra: by[s["url"]]=s
obj["sources"]=list(by.values())
SOURCE.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

reg=json.loads(REGISTRY.read_text(encoding="utf-8"))
m=reg.setdefault("sources",{})
for url,cid in URLS.items():
    k=key(url)
    old=m.get(k)
    if old not in (None,cid): raise SystemExit(f"collision {k}: {old} != {cid}")
    m[k]=cid
REGISTRY.write_text(json.dumps(reg,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print({key(u):cid for u,cid in URLS.items()})
