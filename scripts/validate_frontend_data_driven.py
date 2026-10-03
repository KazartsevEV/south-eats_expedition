#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
CDN = PUBLIC / "cdn" / "v2"
INDEX = PUBLIC / "index.html"

latest = json.loads((CDN / "latest.json").read_text(encoding="utf-8"))
release = CDN / latest["release_id"]
search = json.loads((release / "search" / "global.json").read_text(encoding="utf-8"))
html = INDEX.read_text(encoding="utf-8")

errors = []

# The SPA may know the object-ID syntax, but must never contain concrete object IDs.
literal_ids = sorted(set(re.findall(r"obj_[a-z]{2}_[0-9]{4}", html)))
if literal_ids:
    errors.append("concrete object IDs hardcoded in frontend: " + ", ".join(literal_ids[:20]))

# Long object titles are data, not UI copy. Catch accidental copy/paste of card content.
for row in search.get("objects") or []:
    title = str(row.get("title") or "").strip()
    if len(title) >= 24 and title in html:
        errors.append(f"object title hardcoded in frontend: {title!r}")

# Full cards must be fetched from canonical object JSON through the generic detail() route.
required_fragments = [
    "async function detail(id)",
    "CDN+state.release+'/objects/'+ccOf(id)+'/'+id+'.json'",
    "if(p[0]==='object'&&p[1])return renderObject(p[1])",
]
for fragment in required_fragments:
    if fragment not in html:
        errors.append("missing generic JSON-driven object renderer fragment: " + fragment)

if errors:
    raise SystemExit("\n".join(errors))

print(json.dumps({
    "status": "ok",
    "release_id": latest["release_id"],
    "objects_checked": len(search.get("objects") or []),
    "frontend": "json-driven",
}, ensure_ascii=False))
