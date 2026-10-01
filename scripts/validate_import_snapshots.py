#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMPORT_ROOT = ROOT / "imports" / "google-drive"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def resolve_under(base: Path, relative: str, allowed_root: Path) -> Path:
    path = (base / relative).resolve()
    root = allowed_root.resolve()
    if path != root and root not in path.parents:
        raise ValueError(f"path escapes allowed root: {relative}")
    return path


def descend(value, path_parts):
    current = value
    for part in path_parts:
        if not isinstance(current, dict) or part not in current:
            raise KeyError(".".join(path_parts))
        current = current[part]
    return current


def validate_audit(audit_path: Path) -> list[str]:
    errors: list[str] = []
    audit = load_json(audit_path)
    base = audit_path.parent

    try:
        snapshot = resolve_under(base, audit["snapshot_root"], IMPORT_ROOT)
    except (KeyError, ValueError) as exc:
        return [f"{audit_path}: invalid snapshot_root: {exc}"]

    manifest_name = audit.get("manifest", "manifest.json")
    manifest_path = snapshot / manifest_name
    if not manifest_path.is_file():
        return [f"{audit_path}: manifest missing: {manifest_path}"]

    manifest_bytes = manifest_path.read_bytes()
    expected_manifest_sha = audit.get("manifest_sha256")
    actual_manifest_sha = sha256_bytes(manifest_bytes)
    if expected_manifest_sha and actual_manifest_sha != expected_manifest_sha:
        errors.append(
            f"{audit_path}: manifest sha256 mismatch: "
            f"expected {expected_manifest_sha}, got {actual_manifest_sha}"
        )

    manifest = json.loads(manifest_bytes.decode("utf-8"))
    entries = manifest.get("files")
    if not isinstance(entries, list):
        return errors + [f"{audit_path}: manifest.files must be an array"]

    expected_entries = audit.get("manifest_entries")
    if expected_entries is not None and len(entries) != expected_entries:
        errors.append(
            f"{audit_path}: manifest entry count mismatch: "
            f"expected {expected_entries}, got {len(entries)}"
        )

    by_path = {}
    for entry in entries:
        path = entry.get("path") if isinstance(entry, dict) else None
        if not path or path in by_path:
            errors.append(f"{audit_path}: invalid or duplicate manifest path: {path!r}")
            continue
        by_path[path] = entry

    declared_rows = audit.get("declared_missing_files", [])
    declared = {}
    for row in declared_rows:
        path = row.get("path") if isinstance(row, dict) else None
        if not path or path in declared:
            errors.append(f"{audit_path}: invalid or duplicate declared missing path: {path!r}")
            continue
        declared[path] = row
        expected = by_path.get(path)
        if expected is None:
            errors.append(f"{audit_path}: declared missing path not present in manifest: {path}")
            continue
        for field in ("bytes", "sha256", "cache_class"):
            if row.get(field) != expected.get(field):
                errors.append(
                    f"{audit_path}: declared metadata mismatch for {path} field {field}: "
                    f"{row.get(field)!r} != {expected.get(field)!r}"
                )

    actual_missing: set[str] = set()
    exact_present = 0
    for path, entry in by_path.items():
        try:
            file_path = resolve_under(snapshot, path, snapshot)
        except ValueError as exc:
            errors.append(f"{audit_path}: unsafe manifest path {path}: {exc}")
            continue
        if not file_path.is_file():
            actual_missing.add(path)
            continue

        data = file_path.read_bytes()
        actual_size = len(data)
        actual_sha = sha256_bytes(data)
        if actual_size != entry.get("bytes"):
            errors.append(
                f"{audit_path}: byte-size mismatch for {path}: "
                f"expected {entry.get('bytes')}, got {actual_size}"
            )
            continue
        if actual_sha != entry.get("sha256"):
            errors.append(
                f"{audit_path}: sha256 mismatch for {path}: "
                f"expected {entry.get('sha256')}, got {actual_sha}"
            )
            continue
        exact_present += 1

    declared_set = set(declared)
    if actual_missing != declared_set:
        undeclared = sorted(actual_missing - declared_set)
        stale = sorted(declared_set - actual_missing)
        if undeclared:
            errors.append(
                f"{audit_path}: undeclared missing manifest files: " + ", ".join(undeclared)
            )
        if stale:
            errors.append(
                f"{audit_path}: declared missing files now exist; update audit: " + ", ".join(stale)
            )

    expected_exact = audit.get("exact_entries_present")
    if expected_exact is not None and exact_present != expected_exact:
        errors.append(
            f"{audit_path}: exact present count mismatch: expected {expected_exact}, got {exact_present}"
        )

    for check in audit.get("evidence_checks", []):
        try:
            evidence_path = resolve_under(base, check["path"], IMPORT_ROOT)
            payload = load_json(evidence_path)
            value = descend(payload, check.get("json_path", []))
            expected_count = check["expected_count"]
            actual_count = len(value)
            if actual_count != expected_count:
                errors.append(
                    f"{audit_path}: evidence count mismatch at {check['path']} "
                    f"{'.'.join(check.get('json_path', []))}: "
                    f"expected {expected_count}, got {actual_count}"
                )
        except (KeyError, TypeError, OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"{audit_path}: evidence check failed: {exc}")

    if not errors:
        print(
            f"OK {audit_path.relative_to(ROOT)}: "
            f"{exact_present}/{len(entries)} manifest entries exact; "
            f"{len(actual_missing)} declared historical gaps"
        )
    return errors


def main() -> int:
    if not IMPORT_ROOT.exists():
        print("No Google Drive import root; nothing to validate.")
        return 0

    audits = sorted(IMPORT_ROOT.rglob("*-integrity.json"))
    if not audits:
        print("No import integrity audit files found; nothing to validate.")
        return 0

    errors: list[str] = []
    for audit in audits:
        errors.extend(validate_audit(audit))

    if errors:
        for error in errors:
            print(f"ERROR {error}", file=sys.stderr)
        return 1

    print(f"Validated {len(audits)} import integrity audit(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
