import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.pngutil import segment_rgb, write_rgb
from validator.metadata_panoptic import validate


class MetadataPanopticTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.delivery = Path(self.temp_dir.name)
        (self.delivery / "masks").mkdir()

        self.metadata_items = [
            {
                "image": "alpha.jpg",
                "scene_id": "scene_a",
                "split": "train",
                "job_id": "job_a",
                "guideline_version": "v1.2",
            }
        ]
        self.categories = [{"id": 1, "name": "object", "isthing": 1}]
        self.annotations = [
            {
                "file_name": "alpha.png",
                "segments_info": [
                    {"id": 7, "category_id": 1, "area": 4}
                ],
            }
        ]
        self.write_mask("alpha.png", [7, 7, 7, 7])
        self.write_metadata()
        self.write_jobs()
        self.write_panoptic()

    def tearDown(self):
        self.temp_dir.cleanup()

    def write_metadata(self):
        (self.delivery / "metadata.json").write_text(
            json.dumps({"items": self.metadata_items}), encoding="utf-8"
        )

    def write_jobs(self):
        with (self.delivery / "jobs.csv").open(
            "w", encoding="utf-8", newline=""
        ) as handle:
            writer = csv.DictWriter(handle, fieldnames=["job_id", "guideline"])
            writer.writeheader()
            writer.writerow({"job_id": "job_a", "guideline": "v1.2"})

    def write_panoptic(self):
        (self.delivery / "panoptic.json").write_text(
            json.dumps(
                {
                    "categories": self.categories,
                    "annotations": self.annotations,
                }
            ),
            encoding="utf-8",
        )

    def write_mask(self, filename, segment_ids):
        pixels = bytearray()
        for segment in segment_ids:
            pixels.extend(segment_rgb(segment))
        write_rgb(self.delivery / "masks" / filename, 2, 2, pixels)

    def test_detects_scene_leak_once_per_scene(self):
        self.metadata_items.append(
            {
                "image": "beta.jpg",
                "scene_id": "scene_a",
                "split": "val",
                "job_id": "job_a",
                "guideline_version": "v1.2",
            }
        )
        self.write_metadata()

        self.assertIn(
            {"type": "scene_leak", "target": "scene_a"},
            validate(self.delivery),
        )

    def test_detects_guideline_mismatch_using_job_guideline(self):
        self.metadata_items[0]["guideline_version"] = "v1.3"
        self.write_metadata()

        self.assertIn(
            {"type": "guideline_mismatch", "target": "alpha"},
            validate(self.delivery),
        )

    def test_detects_category_id_missing_from_categories(self):
        self.annotations[0]["segments_info"][0]["category_id"] = 99
        self.write_panoptic()

        self.assertIn(
            {"type": "invalid_category_id", "target": "alpha"},
            validate(self.delivery),
        )

    def test_detects_thing_area_larger_than_mask_pixel_count(self):
        self.annotations[0]["segments_info"][0]["area"] = 5
        self.write_panoptic()

        self.assertIn(
            {"type": "thing_overlap", "target": "alpha"},
            validate(self.delivery),
        )

    def test_does_not_flag_correct_thing_area_or_stuff_area(self):
        self.categories[0]["isthing"] = 0
        self.annotations[0]["segments_info"][0]["area"] = 5
        self.write_panoptic()

        self.assertEqual(validate(self.delivery), [])

    def test_ignores_background_pixels_when_counting_segments(self):
        self.write_mask("alpha.png", [7, 7, 7, 0])
        self.annotations[0]["segments_info"][0]["area"] = 3
        self.write_panoptic()

        self.assertEqual(validate(self.delivery), [])


if __name__ == "__main__":
    unittest.main()
