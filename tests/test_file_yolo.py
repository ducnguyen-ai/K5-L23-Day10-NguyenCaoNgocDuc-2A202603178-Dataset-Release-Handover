"""Synthetic regression cases for Person 1, with no source data or answer keys."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from validator.file_yolo import validate


class FileYoloTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        for folder in ("images", "labels", "masks"):
            (self.root / folder).mkdir()
        (self.root / "classes.txt").write_text("0 person\n1 bicycle\n", encoding="utf-8")
        (self.root / "images/a.jpg").write_bytes(b"synthetic image bytes")
        (self.root / "masks/a.png").write_bytes(b"synthetic mask bytes")
        (self.root / "panoptic.json").write_text(json.dumps({"images": [
            {"id": 1, "file_name": "a.jpg", "width": 640, "height": 480}
        ]}), encoding="utf-8")
        self.set_labels("0 0.5 0.5 0.2 0.2\n")

    def set_labels(self, text):
        (self.root / "labels/a.txt").write_text(text, encoding="utf-8")
        item = {"image": "images/a.jpg", "label": "labels/a.txt", "mask": "masks/a.png"}
        for kind in ("image", "label", "mask"):
            item[kind + "_sha256"] = hashlib.sha256((self.root / item[kind]).read_bytes()).hexdigest()
        (self.root / "manifest.json").write_text(json.dumps({"items": {"a": item}}), encoding="utf-8")

    def types(self):
        return {error["type"] for error in validate(self.root)}

    def test_valid_and_six_decimal_boundary_rounding(self):
        self.set_labels("0 0.1 0.5 0.200001 1.0\n")
        self.assertEqual(self.types(), set())

    def test_hash_compares_content_for_all_manifest_file_types(self):
        for kind in ("images/a.jpg", "labels/a.txt", "masks/a.png"):
            with self.subTest(kind=kind):
                path = self.root / kind
                before = path.read_bytes()
                path.write_bytes(before + b"\n")
                self.assertIn("wrong_hash", self.types())
                path.write_bytes(before)

    def test_missing_image_is_not_also_a_hash_mismatch(self):
        (self.root / "images/a.jpg").unlink()
        self.assertEqual(self.types(), {"missing_image"})

    def test_invalid_and_noninteger_classes(self):
        for class_id in ("2", "-1", "0.5", "nan"):
            with self.subTest(class_id=class_id):
                self.set_labels(f"{class_id} 0.5 0.5 0.2 0.2\n")
                self.assertEqual(self.types(), {"invalid_class"})

    def test_small_boundary_overrun_and_nonfinite_box(self):
        for coordinates in ("0.099998 0.5 0.2 0.2", "nan 0.5 0.2 0.2", "0.5 0.5 -0.2 0.2"):
            with self.subTest(coordinates=coordinates):
                self.set_labels(f"0 {coordinates}\n")
                self.assertEqual(self.types(), {"bbox_out_of_bounds"})

    def test_duplicate_same_size_two_pixel_center_shift(self):
        self.set_labels("0 0.5 0.5 0.2 0.2\n0 0.503125 0.5 0.2 0.2\n")
        self.assertEqual(self.types(), {"duplicate_box"})

    def test_naturally_overlapping_objects_are_not_duplicates(self):
        self.set_labels("0 0.5 0.5 0.2 0.2\n0 0.5 0.5 0.21 0.21\n1 0.5 0.5 0.2 0.2\n")
        self.assertEqual(self.types(), set())

    def test_manifest_cannot_reference_a_parent_directory(self):
        path = self.root / "manifest.json"
        data = json.loads(path.read_text())
        data["items"]["a"]["image"] = "../outside.jpg"
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, "outside delivery"):
            validate(self.root)


if __name__ == "__main__":
    unittest.main()
