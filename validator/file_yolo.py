"""Person 1: file integrity and YOLO checks using delivery files only."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

BOUND_TOLERANCE = 1e-6  # YOLO coordinates are rounded to six decimal places.
DUPLICATE_CENTER_PX = 2.01
DUPLICATE_SIZE_PX = 0.01


def delivery_path(root: Path, relative: str) -> Path:
    """Resolve a manifest path without allowing reads outside the delivery."""
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f"Manifest path outside delivery: {relative}")
    return path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_classes(root: Path) -> set[int]:
    ids = set()
    for line in (root / "classes.txt").read_text(encoding="utf-8-sig").splitlines():
        if line.strip():
            index, name = line.split(maxsplit=1)
            class_id = int(index)
            if class_id in ids or not name.strip():
                raise ValueError("Invalid or duplicate class declaration")
            ids.add(class_id)
    if not ids:
        raise ValueError("classes.txt is empty")
    return ids


def read_dimensions(root: Path) -> dict[str, tuple[int, int]]:
    # Read image dimensions, not segment annotations. Missing images still have dimensions.
    data = json.loads((root / "panoptic.json").read_text(encoding="utf-8-sig"))
    sizes = {}
    for image in data["images"]:
        width, height = int(image["width"]), int(image["height"])
        if width <= 0 or height <= 0:
            raise ValueError(f"Invalid dimensions: {image['file_name']}")
        sizes[Path(image["file_name"]).name] = (width, height)
    return sizes


def is_duplicate(first: tuple, second: tuple, size: tuple[int, int]) -> bool:
    if first[0] != second[0]:
        return False
    width, height = size
    return (
        abs(first[3] - second[3]) * width <= DUPLICATE_SIZE_PX
        and abs(first[4] - second[4]) * height <= DUPLICATE_SIZE_PX
        and abs(first[1] - second[1]) * width <= DUPLICATE_CENTER_PX
        and abs(first[2] - second[2]) * height <= DUPLICATE_CENTER_PX
    )


def validate(delivery: Path) -> list[dict[str, str]]:
    root = delivery.resolve(strict=True)
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8-sig"))
    classes = read_classes(root)
    dimensions = read_dimensions(root)
    findings: set[tuple[str, str]] = set()
    for target, item in manifest["items"].items():
        image = delivery_path(root, item["image"])
        if not image.is_file():
            findings.add(("missing_image", target))
        for kind in ("image", "label", "mask"):
            path = delivery_path(root, item[kind])
            expected = item.get(kind + "_sha256")
            if path.is_file() and expected and sha256(path).lower() != expected.lower():
                findings.add(("wrong_hash", target))

        label = delivery_path(root, item["label"])
        if not label.is_file():
            raise ValueError(f"Missing YOLO label file: {item['label']}")
        size = dimensions.get(image.name)
        if size is None:
            raise ValueError(f"Missing image dimensions in panoptic.json: {image.name}")
        boxes = []
        for line_number, line in enumerate(label.read_text(encoding="utf-8-sig").splitlines(), 1):
            if not line.strip():
                continue
            fields = line.split()
            if len(fields) != 5:
                raise ValueError(f"{item['label']}:{line_number}: expected five YOLO fields")
            try:
                class_id = int(fields[0])
            except ValueError:
                class_id = None
            if class_id not in classes:
                findings.add(("invalid_class", target))
            try:
                cx, cy, width, height = map(float, fields[1:])
            except ValueError as error:
                raise ValueError(f"{item['label']}:{line_number}: nonnumeric coordinates") from error
            finite = all(math.isfinite(v) for v in (cx, cy, width, height))
            if not finite:
                findings.add(("bbox_out_of_bounds", target))
                continue
            if (width <= 0 or height <= 0
                or cx - width / 2 < -BOUND_TOLERANCE
                or cy - height / 2 < -BOUND_TOLERANCE
                or cx + width / 2 > 1 + BOUND_TOLERANCE
                or cy + height / 2 > 1 + BOUND_TOLERANCE):
                findings.add(("bbox_out_of_bounds", target))
            if class_id in classes:
                box = (class_id, cx, cy, width, height)
                if any(is_duplicate(box, previous, size) for previous in boxes):
                    findings.add(("duplicate_box", target))
                boxes.append(box)
    return [{"type": kind, "target": target} for kind, target in sorted(findings)]
