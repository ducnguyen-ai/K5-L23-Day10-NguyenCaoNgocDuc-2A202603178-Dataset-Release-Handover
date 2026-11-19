"""Person 3 candidate generator: inspect, calibrate, and human-review all findings.

This is a conservative STARTING BASELINE, not a validated detector or answer key.
Only standard-library imports + the repository's scripts/pngutil.py are used.
Contract: generate_candidates(delivery: pathlib.Path) -> list[dict].
"""
from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path

from scripts.pngutil import read_rgb, segment_id

# Calibrate using the clean pool and visual reviews, never _private or truth dirs.
MIN_SEGMENT_PIXELS = 64
MATCH_SEGMENT_COVERAGE = 0.45
DRIFT_SEGMENT_COVERAGE = 0.80
MERGE_BOX_COVERAGE = 0.50


def _inside(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f"Path outside delivery: {relative}")
    return path


def _classes(root: Path) -> dict[int, str]:
    result = {}
    for line in _inside(root, "classes.txt").read_text(encoding="utf-8-sig").splitlines():
        if line.strip():
            number, name = line.split(maxsplit=1)
            result[int(number)] = name.strip()
    return result


def _yolo_boxes(root: Path, label_relative: str, size: tuple[int, int], classes: dict):
    width, height = size
    label = _inside(root, label_relative)
    if not label.exists():
        return []
    boxes = []
    for index, line in enumerate(label.read_text(encoding="utf-8-sig").splitlines()):
        if not line.strip():
            continue
        fields = line.split()
        if len(fields) != 5:
            continue  # File/YOLO validator reports malformed rows separately.
        try:
            class_id = int(fields[0])
            cx, cy, bw, bh = (float(v) for v in fields[1:])
        except ValueError:
            continue
        if class_id not in classes or not all(map(math.isfinite, (cx, cy, bw, bh))):
            continue
        if bw <= 0 or bh <= 0:
            continue
        x0 = max(0, min(width, math.floor((cx - bw / 2) * width)))
        x1 = max(0, min(width, math.ceil((cx + bw / 2) * width)))
        y0 = max(0, min(height, math.floor((cy - bh / 2) * height)))
        y1 = max(0, min(height, math.ceil((cy + bh / 2) * height)))
        if x1 > x0 and y1 > y0:
            boxes.append({"index": index, "class": classes[class_id], "rect": (x0, y0, x1, y1)})
    return boxes


def _segment_bounds(width: int, height: int, pixels: bytes):
    """Count real segment pixels and calculate tight bounds; id 0 is background."""
    stats = {}
    for y in range(height):
        for x in range(width):
            sid = segment_id(pixels, (y * width + x) * 3)
            if sid == 0:
                continue
            if sid not in stats:
                stats[sid] = {"area": 0, "rect": [x, y, x + 1, y + 1]}
            row = stats[sid]
            row["area"] += 1
            rect = row["rect"]
            rect[0], rect[1] = min(rect[0], x), min(rect[1], y)
            rect[2], rect[3] = max(rect[2], x + 1), max(rect[3], y + 1)
    return stats


def _mask_overlap(width: int, pixels: bytes, sid: int, bounds: list[int], box: tuple[int, ...]) -> int:
    x0, y0 = max(bounds[0], box[0]), max(bounds[1], box[1])
    x1, y1 = min(bounds[2], box[2]), min(bounds[3], box[3])
    if x1 <= x0 or y1 <= y0:
        return 0
    overlap = 0
    for y in range(y0, y1):
        for x in range(x0, x1):
            if segment_id(pixels, (y * width + x) * 3) == sid:
                overlap += 1
    return overlap


def _candidate(kind: str, image: str, sid: int, box, evidence: dict, location):
    result = {
        "type": kind, "image": image, "target": image,
        "segment_id": sid, "location": list(location), "evidence": evidence,
    }
    if box is not None:
        result["box_index"] = box["index"]
    return result


def generate_candidates(delivery: Path) -> list[dict]:
    """Return candidate records. None is automatically a confirmed error."""
    root = Path(delivery).resolve(strict=True)
    classes = _classes(root)
    panoptic = json.loads(_inside(root, "panoptic.json").read_text(encoding="utf-8-sig"))
    manifest = json.loads(_inside(root, "manifest.json").read_text(encoding="utf-8-sig"))
    by_image_id = {image["id"]: image for image in panoptic["images"]}
    categories = {cat["id"]: cat for cat in panoptic["categories"]}
    candidates = []
    seen = set()

    def add(record):
        key = (record["image"], record["type"], record.get("box_index"), record["segment_id"])
        if key not in seen:
            seen.add(key)
            candidates.append(record)

    for ann in panoptic["annotations"]:
        image_info = by_image_id[ann["image_id"]]
        stem = Path(image_info["file_name"]).stem
        mask_path = _inside(root, str(Path("masks") / ann["file_name"]))
        if not mask_path.is_file():
            continue
        width, height, pixels = read_rgb(mask_path)
        if (width, height) != (image_info["width"], image_info["height"]):
            raise ValueError(f"Mask and image dimensions differ: {stem}")
        manifest_item = manifest["items"].get(stem, {})
        label_relative = manifest_item.get("label", f"labels/{stem}.txt")
        boxes = _yolo_boxes(root, label_relative, (width, height), classes)
        stats = _segment_bounds(width, height, pixels)

        for seg in ann["segments_info"]:
            sid = seg["id"]
            cat = categories.get(seg["category_id"])
            if sid == 0 or cat is None or cat.get("isthing") != 1 or seg.get("iscrowd", 0):
                continue
            actual = stats.get(sid)
            if actual is None or actual["area"] < MIN_SEGMENT_PIXELS:
                continue
            seg_name = cat["name"]
            matches = []
            for box in boxes:
                intersect = _mask_overlap(width, pixels, sid, actual["rect"], box["rect"])
                if not intersect:
                    continue
                box_area = (box["rect"][2] - box["rect"][0]) * (box["rect"][3] - box["rect"][1])
                matches.append((box, intersect / actual["area"], intersect / box_area))
            matches.sort(key=lambda match: (match[1], match[2]), reverse=True)

            # One panoptic segment covering two same-class detection boxes can be a merge.
            merge_boxes = [b for b, _, box_cover in matches
                           if b["class"] == seg_name and box_cover >= MERGE_BOX_COVERAGE]
            if len(merge_boxes) >= 2:
                add(_candidate("instance_merge", stem, sid, merge_boxes[0],
                               {"segment_class": seg_name, "box_indices": [b["index"] for b in merge_boxes]},
                               actual["rect"]))

            if not matches or matches[0][1] < MATCH_SEGMENT_COVERAGE:
                add(_candidate("missing_box", stem, sid, None,
                               {"segment_class": seg_name, "actual_pixels": actual["area"],
                                "best_segment_coverage": round(matches[0][1], 3) if matches else 0},
                               actual["rect"]))
                continue

            best, seg_cover, box_cover = matches[0]
            if best["class"] != seg_name:
                suspect = _candidate("class_swap", stem, sid, best,
                                     {"detection_class": best["class"], "panoptic_class": seg_name,
                                      "segment_coverage": round(seg_cover, 3),
                                      "box_coverage": round(box_cover, 3)}, actual["rect"])
                # Human decides which source is wrong before writing review_log.csv.
                suspect["possible_types"] = ["class_swap", "category_swap"]
                add(suspect)
            elif seg_cover < DRIFT_SEGMENT_COVERAGE:
                add(_candidate("bbox_drift", stem, sid, best,
                               {"class": seg_name, "segment_coverage": round(seg_cover, 3),
                                "box_coverage": round(box_cover, 3)}, actual["rect"]))

    return sorted(candidates, key=lambda row: (row["image"], row["type"],
                                                row.get("segment_id", -1), row.get("box_index", -1)))
