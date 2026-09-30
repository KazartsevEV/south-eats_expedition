#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path

from build_cdn import RELEASE_ID as BUILD_RELEASE_ID


def load(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def get_release_context(public_root: Path):
    """
    Select the release being built/validated without changing latest.json.

    EXPEDITION_RELEASE_ID is an explicit override for maintenance runs.
    Otherwise the active build target from build_cdn.py is authoritative.
    """
    root = Path(public_root)
    release_id = os.environ.get("EXPEDITION_RELEASE_ID") or BUILD_RELEASE_ID
    release = root / release_id
    manifest_path = release / "manifest.json"
    if not manifest_path.exists():
        raise RuntimeError(
            f"build target {release_id!r} has no manifest at {manifest_path}; "
            "run build_cdn.py first or set EXPEDITION_RELEASE_ID explicitly"
        )
    manifest = load(manifest_path)
    if manifest.get("release_id") != release_id:
        raise RuntimeError(
            f"build target/manifest mismatch: {release_id!r} != {manifest.get('release_id')!r}"
        )
    schema_version = manifest.get("schema_version")
    if not schema_version:
        raise RuntimeError(f"manifest for {release_id!r} lacks schema_version")
    return {
        "release_id": release_id,
        "schema_version": schema_version,
        "release": release,
        "manifest": manifest,
    }


def validate_latest_pointer(public_root: Path):
    """Validate the promoted reference pointer independently of the build target."""
    root = Path(public_root)
    latest_path = root / "latest.json"
    if not latest_path.exists():
        raise RuntimeError(f"missing promoted release pointer: {latest_path}")
    latest = load(latest_path)
    release_id = latest.get("release_id")
    if not release_id:
        raise RuntimeError("latest.json missing release_id")
    manifest_path = root / release_id / "manifest.json"
    if not manifest_path.exists():
        raise RuntimeError(f"latest.json points to missing manifest: {manifest_path}")
    manifest = load(manifest_path)
    if manifest.get("release_id") != release_id:
        raise RuntimeError("latest/manifest release_id mismatch")
    if manifest.get("schema_version") != latest.get("schema_version"):
        raise RuntimeError("latest/manifest schema_version mismatch")
    return latest
