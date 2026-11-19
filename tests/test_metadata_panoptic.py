"""Synthetic-only regression tests. No downloads, _private, or source labels."""
import csv
import json
import tempfile
import unittest
from pathlib import Path

from scripts.pngutil import segment_rgb, write_rgb
from validator.metadata_panoptic import validate


class MetadataPanopticTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "masks").mkdir()

        self.metadata = {"items": [
            {"image": "a", "scene_id": "scene_x", "split": "train", "job_id": "J01", "guideline_version": "v1"},
            {"image": "b", "scene_id": "scene_x", "split": "train", "job_id": "J01", "guideline_version": "v1"},
        ]}
        self.panoptic = {
            "categories": [{"id": 1, "name": "person", "isthing": 1}],
            "images": [{"id": 1, "file_name": "a.jpg", "width": 32, "height": 32}],
            "annotations": [{"image_id": 1, "file_name": "a.png", "segments_info": [
                {"id": 7, "category_id": 1, "area": 144, "iscrowd": 0}
            ]}],
        }
        mask = bytearray(32 * 32 * 3)
        rgb = segment_rgb(7)
        for y in range(4, 16):
            for x in range(4, 16):
                pos = (y * 32 + x) * 3
                mask[pos:pos + 3] = bytes(rgb)
        write_rgb(self.root / "masks/a.png", 32, 32, mask)
        with (self.root / "jobs.csv").open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=["job_id", "guideline"])
            writer.writeheader()
            writer.writerow({"job_id": "J01", "guideline": "v1"})
        self.save()

    def save(self):
        (self.root / "metadata.json").write_text(json.dumps(self.metadata), encoding="utf-8")
        (self.root / "panoptic.json").write_text(json.dumps(self.panoptic), encoding="utf-8")

    def test_clean_synthetic_delivery(self):
        self.assertEqual(validate(self.root), [])

    def test_detects_all_four_rules_and_deduplicates_targets(self):
        self.metadata["items"][1]["split"] = "val"
        self.metadata["items"][0]["guideline_version"] = "v0"
        self.panoptic["annotations"][0]["segments_info"][0]["area"] = 150
        self.panoptic["annotations"][0]["segments_info"].append(
            {"id": 9, "category_id": 999, "area": 1, "iscrowd": 0}
        )
        self.save()
        result = {(row["type"], row["target"]) for row in validate(self.root)}
        self.assertEqual(result, {
            ("scene_leak", "scene_x"), ("guideline_mismatch", "a"),
            ("thing_overlap", "a"), ("invalid_category_id", "a"),
        })


if __name__ == "__main__":
    unittest.main()
