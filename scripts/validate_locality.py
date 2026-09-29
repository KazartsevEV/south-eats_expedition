#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


LOCAL_PROFILE_KEYS = {
    "dangerous_animals",
    "poisonous_plants",
    "tides",
    "marine",
    "local_crime",
    "diseases",
}
LOCAL_CLIMATE_KEYS = {
    "sea_temp_mean_c_by_month",
    "tides",
    "marine",
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def walk(value, path=()):
    if isinstance(value, dict):
        for key, child in value.items():
            yield path + (key,), child
            yield from walk(child, path + (key,))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk(child, path + (str(index),))


parser = argparse.ArgumentParser()
parser.add_argument("root", nargs="?", default="public/cdn/v2")
parser.add_argument("--strict", action="store_true")
args = parser.parse_args()

root = Path(args.root)
latest = load(root / "latest.json")
release = root / latest["release_id"]
findings = []

for path in sorted((release / "countries").glob("*/profile.json")):
    value = load(path)
    for key_path, child in walk(value):
        if key_path[-1] in LOCAL_PROFILE_KEYS and child not in (None, [], {}, ""):
            findings.append({
                "file": path.relative_to(release).as_posix(),
                "field": ".".join(key_path),
            })

for path in sorted((release / "countries").glob("*/climate.json")):
    value = load(path)
    for key_path, child in walk(value):
        if key_path[-1] in LOCAL_CLIMATE_KEYS and child not in (None, [], {}, ""):
            findings.append({
                "file": path.relative_to(release).as_posix(),
                "field": ".".join(key_path),
            })

result = {
    "status": "needs_migration" if findings else "ok",
    "release_id": latest["release_id"],
    "country_locality_findings": len(findings),
    "findings": findings,
    "rule": "country=macro context; geo=local climate/nature/safety facts",
}
print(json.dumps(result, ensure_ascii=False, indent=2))

if args.strict and findings:
    raise SystemExit(1)
