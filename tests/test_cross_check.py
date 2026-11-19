"""Synthetic checks for cross_check's interface and basic candidate signals."""
import json
import tempfile
import unittest
from pathlib import Path

from scripts.pngutil import segment_rgb, write_rgb
from validator.cross_check import generate_candidates


class CrossCheckTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "labels").mkdir()
        (self.root / "masks").mkdir()
        (self.root / "classes.txt").write_text("0 person\n1 car\n", encoding="utf-8")
        self.panoptic = {
            "categories": [{"id": 1, "name": "person", "isthing": 1},
                           {"id": 2, "name": "car", "isthing": 1}],
            "images": [{"id": 1, "file_name": "a.jpg", "width": 32, "height": 32}],
            "annotations": [{"image_id": 1, "file_name": "a.png", "segments_info": [
                {"id": 7, "category_id": 1, "area": 144, "iscrowd": 0}
            ]}],
        }
        (self.root / "manifest.json").write_text(json.dumps({"items": {
            "a": {"label": "labels/a.txt"}
        }}), encoding="utf-8")
        self.mask = bytearray(32 * 32 * 3)
        rgb = segment_rgb(7)
        for y in range(4, 16):
            for x in range(4, 16):
                index = (y * 32 + x) * 3
                self.mask[index:index + 3] = bytes(rgb)
        write_rgb(self.root / "masks/a.png", 32, 32, self.mask)
        self._save_panoptic()
        self.label("0 0.3125 0.3125 0.375 0.375\n")

    def _save_panoptic(self):
        (self.root / "panoptic.json").write_text(json.dumps(self.panoptic), encoding="utf-8")

    def label(self, contents):
        (self.root / "labels/a.txt").write_text(contents, encoding="utf-8")

    def types(self):
        return {item["type"] for item in generate_candidates(self.root)}

    def test_matching_clean_instance(self):
        self.assertEqual(self.types(), set())

    def test_class_disagreement_requires_human_to_choose_type(self):
        self.label("1 0.3125 0.3125 0.375 0.375\n")
        cases = generate_candidates(self.root)
        self.assertEqual([row["type"] for row in cases], ["class_swap"])
        self.assertEqual(cases[0]["possible_types"], ["class_swap", "category_swap"])

    def test_missing_box(self):
        self.label("")
        self.assertEqual(self.types(), {"missing_box"})

    def test_bbox_drift(self):
        self.label("0 0.46875 0.3125 0.375 0.375\n")
        self.assertIn("bbox_drift", self.types())

    def test_instance_merge(self):
        self.label("0 0.21875 0.3125 0.1875 0.375\n0 0.40625 0.3125 0.1875 0.375\n")
        self.assertIn("instance_merge", self.types())


if __name__ == "__main__":
    unittest.main()
