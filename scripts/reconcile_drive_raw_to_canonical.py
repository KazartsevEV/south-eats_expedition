#!/usr/bin/env python3
"""Read-only guardrail for Drive-raw -> canonical object/source reconciliation."""
from __future__ import annotations
import argparse, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PROVEN_RENAMES={
    ("BN","Tutong and Tamu markets"): ("BN","Pasarneka Tutong / Tamu Tutong"),
}

def load(p:Path):
    with p.open("r",encoding="utf-8") as f:
        return json.load(f)

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
    reconciled_raw={PROVEN_RENAMES.get(key,key) for key in raw_keys}
    missing=sorted(reconciled_raw-canonical)
    extra=sorted(canonical-reconciled_raw)

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
        "proven_renames":[{"raw":list(k),"canonical":list(v)} for k,v in PROVEN_RENAMES.items()],
        "unresolved_raw_objects":missing,
        "unexplained_canonical_objects":extra,
        "raw_source_urls_missing_from_canonical":missing_urls,
    },ensure_ascii=False,indent=2))
    if missing or extra:
        raise SystemExit(2)

if __name__=="__main__":
    main()
