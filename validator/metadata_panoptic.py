
"""Person 2: metadata and panoptic rule checks."""
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

from scripts.pngutil import read_rgb, segment_id


def delivery_file(root: Path, relative_path: str) -> Path:
    """Resolve a path and prevent reading outside delivery."""
    path = (root / relative_path).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f"Path outside delivery: {relative_path}")
    return path


def validate(delivery: Path) -> list[dict[str, str]]:
    root = delivery.resolve(strict=True)
    findings = set()

    # 1. Read metadata and jobs.
    metadata = json.loads(
        delivery_file(root, "metadata.json").read_text(encoding="utf-8-sig")
    )

    with delivery_file(root, "jobs.csv").open(
        "r", encoding="utf-8-sig", newline=""
    ) as handle:
        jobs = {
            row["job_id"]: row["guideline"]
            for row in csv.DictReader(handle)
        }

    # 2. scene_leak and guideline_mismatch.
    scene_splits = defaultdict(set)

    for item in metadata["items"]:
        scene_splits[item["scene_id"]].add(item["split"])

    for scene_id, splits in scene_splits.items():
        if {"train", "val"}.issubset(splits):
            findings.add(("scene_leak", scene_id))

    for item in metadata["items"]:
        job_id = item["job_id"]

        if job_id in jobs:
            if item["guideline_version"] != jobs[job_id]:
                findings.add(("guideline_mismatch", item["image"]))

    # 3. Read panoptic categories and annotations.
    panoptic = json.loads(
        delivery_file(root, "panoptic.json").read_text(
            encoding="utf-8-sig"
        )
    )

    categories = {
        category["id"]: category
        for category in panoptic["categories"]
    }

    # 4. invalid_category_id and thing_overlap.
    for annotation in panoptic["annotations"]:
        image_name = Path(annotation["file_name"]).stem

        for segment in annotation["segments_info"]:
            category_id = segment["category_id"]

            if category_id not in categories:
                findings.add(("invalid_category_id", image_name))

        mask_relative = str(
            Path("masks") / annotation["file_name"]
        )
        mask_path = delivery_file(root, mask_relative)

        # Missing masks are not classified as thing_overlap.
        if not mask_path.is_file():
            continue

        width, height, pixels = read_rgb(mask_path)

        pixel_counts = Counter(
            segment_id(pixels, index)
            for index in range(0, len(pixels), 3)
        )

        for segment in annotation["segments_info"]:
            segment_value = segment["id"]

            # Ignore background.
            if segment_value == 0:
                continue

            category = categories.get(segment["category_id"])
            if category is None:
                continue

            # Only check thing categories.
            if category.get("isthing") != 1:
                continue

            declared_area = segment["area"]
            actual_area = pixel_counts.get(segment_value, 0)

            if declared_area > actual_area:
                findings.add(("thing_overlap", image_name))

    return [
        {"type": error_type, "target": target}
        for error_type, target in sorted(findings)
    ]
