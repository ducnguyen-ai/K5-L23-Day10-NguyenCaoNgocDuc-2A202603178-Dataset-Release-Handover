"""Command-line integration point for the team's Day10 validator."""
from __future__ import annotations

import argparse
from collections import Counter
import importlib
import json
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from validator.file_yolo import validate as validate_file_yolo


def optional_module(name: str):
    qualified = f"validator.{name}"
    try:
        return importlib.import_module(qualified)
    except ModuleNotFoundError as error:
        if error.name == qualified:
            return None
        raise


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent,
                                         prefix=path.name + ".", suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name)
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("delivery", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--candidates", type=Path)
    args = parser.parse_args()
    delivery = args.delivery.resolve(strict=True)
    outputs = [args.out.resolve()]
    if args.candidates is not None:
        outputs.append(args.candidates.resolve())
    if len(set(outputs)) != len(outputs):
        parser.error("--out and --candidates must be different files")
    if any(path.is_relative_to(delivery) for path in outputs):
        parser.error("Outputs must be outside the input delivery")

    errors = validate_file_yolo(delivery)
    metadata_panoptic = optional_module("metadata_panoptic")
    if metadata_panoptic is not None:
        errors.extend(metadata_panoptic.validate(delivery))
    else:
        print("PENDING: metadata/panoptic checks await team integration; output contains Person 1 checks.", file=sys.stderr)

    pairs = sorted({(item["type"], item["target"]) for item in errors})
    write_json(args.out, {"errors": [{"type": kind, "target": target} for kind, target in pairs]})
    if args.candidates is not None:
        cross_check = optional_module("cross_check")
        if cross_check is not None:
            candidates = cross_check.generate_candidates(delivery)
            write_json(args.candidates, {"candidates": candidates, "status": "generated_for_human_review"})
        else:
            if not args.candidates.exists():
                write_json(args.candidates, {"candidates": [], "status": "pending_cross_check_integration"})
            print("PENDING: cross-check generation awaits team integration. Existing candidate files preserved.", file=sys.stderr)
    print(f"Rule findings: {len(pairs)}; by type: {dict(Counter(kind for kind, _ in pairs))}")
    print(f"Written: {args.out}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError) as error:
        print(f"Validator failed: {error}", file=sys.stderr)
        raise SystemExit(2)
