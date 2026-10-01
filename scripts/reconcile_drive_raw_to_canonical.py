#!/usr/bin/env python3
"""Guardrail for Drive-raw -> canonical reconciliation.

This script is intentionally read-only. It verifies the two non-negotiable
identity/source invariants used by the 2026-10-02 audit:
1) the Drive snapshot and strict canonical search contain the same object names;
2) raw source URLs are either present in canonical sources/index.json or reported.

It does not auto-copy legacy fields. Field migration must follow the canonical
schema and the visual-recon policy.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def load(p:Path):
    with p.open("r",encoding="utf-8") as f: return json.load(f)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--snapshot",default="imports/google-drive/2026-10-01/expedition-south-east")
    ap.add_argument("--release",default="2026-09-30-r42")
    args=ap.parse_args()
    snap=ROOT/args.snapshot
    idx=load(snap/"index.json")
    raw=[]
    for row in idx["countries"]:
        matches=list(snap.rglob(row["file"]))
        if len(matches)!=1:
            raise SystemExit(f"{row['file']}: expected exactly one snapshot file, got {len(matches)}")
        doc=load(matches[0])
        cc=row["country_code"]
        for obj in doc.get("travel",{}).get("objects",[]):
            raw.append((cc,obj["name"],obj))
    release=ROOT/"public"/"cdn"/"v2"/args.release
    search=load(release/"search"/"objects.json")
    canonical={(x["country_code"],x["name"]) for x in search["objects"]}
    raw_keys={(cc,name) for cc,name,_ in raw}
    missing=sorted(raw_keys-canonical)
    extra=sorted(canonical-raw_keys)
    sources=load(release/"sources"/"index.json")
    urls={x.get("url") for x in sources["sources"] if x.get("url")}
    missing_urls=[]
    for cc,name,obj in raw:
        for src in obj.get("sources",[]):
            url=src.get("url")
            if url and url not in urls:
                missing_urls.append({"country_code":cc,"object":name,"url":url})
    print(json.dumps({
        "raw_objects":len(raw_keys),
        "canonical_objects":len(canonical),
        "missing_objects":missing,
        "extra_objects":extra,
        "raw_source_urls_missing_from_canonical":missing_urls,
    },ensure_ascii=False,indent=2))
    if missing or extra:
        raise SystemExit(2)

if __name__=="__main__":
    main()
