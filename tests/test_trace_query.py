"""Synthetic cases for ticket trace criteria; no seed-specific answers."""

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("trace_query", Path(__file__).resolve().parents[1] / "tools" / "trace_query.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class TraceQueryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.delivery = Path(self.temp.name)
        self.put("incoming/ticket.md", "Team AI báo scene_101; đề nghị rà soát.\n")
        self.put("guideline/changelog.md", "## v1.3\n- Lớp `car`: đổi quy tắc (v1.2 cho bỏ).\n## v1.2\nBản cũ.\n")
        self.put("classes.txt", "0 person\n2 car\n20 elephant\n")
        self.put("jobs.csv", "job_id,annotator,reviewer,guideline\nJ1,A1,Q1,v1.2\nJ2,A2,Q1,v1.2\nJ3,A3,Q3,v1.3\n")
        self.items = [
            {"image": "a", "scene_id": "scene_101", "job_id": "J1", "guideline_version": "v1.3"},
            {"image": "b", "scene_id": "scene_202", "job_id": "J2", "guideline_version": "v1.2"},
            {"image": "c", "scene_id": "scene_101", "job_id": "J3", "guideline_version": "v1.2"},
            {"image": "d", "scene_id": "scene_101", "job_id": "J1", "guideline_version": "v1.2"},
        ]
        self.manifest = {item["image"]: {"label": f"labels/{item['image']}.txt"} for item in self.items}
        for name in ("a", "b", "c"):
            self.put(f"labels/{name}.txt", "2 0.5 0.5 0.2 0.2\n2 0.7 0.7 0.1 0.1\n")
        self.put("labels/d.txt", "20 0.5 0.5 0.2 0.2\n")
        self.refresh()

    def put(self, relative, text):
        path = self.delivery / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def refresh(self):
        self.put("metadata.json", json.dumps({"items": self.items}))
        self.put("manifest.json", json.dumps({"items": self.manifest}))
        digest = hashlib.sha256((self.delivery / "manifest.json").read_bytes() + (self.delivery / "metadata.json").read_bytes()).hexdigest()
        self.put("release.json", json.dumps({"release_id": "lab250_" + digest[:12]}))

    def test_uses_job_guideline_despite_wrong_image_guideline(self):
        trace, evidence = MODULE.trace_delivery(self.delivery)
        self.assertEqual(trace["tier_a"], ["a"])
        self.assertEqual(trace["tier_b"], ["b"])
        self.assertEqual(len(evidence["image_job_guideline_mismatches"]), 2)

    def test_exact_class_id_and_deduplicated_people_and_images(self):
        trace, evidence = MODULE.trace_delivery(self.delivery)
        self.assertEqual(trace, {"tier_a": ["a"], "tier_b": ["b"], "notify": ["A1", "A2", "Q1"]})
        self.assertEqual(evidence["selected_images"][0]["matching_label_lines"], [1, 2])

    def test_reads_only_delivery_and_preserves_all_source_bytes(self):
        before = {str(p.relative_to(self.delivery)): p.read_bytes() for p in self.delivery.rglob("*") if p.is_file()}
        MODULE.trace_delivery(self.delivery)
        after = {str(p.relative_to(self.delivery)): p.read_bytes() for p in self.delivery.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_missing_job_does_not_silently_drop_image(self):
        self.items[0]["job_id"] = "UNKNOWN"
        self.refresh()
        with self.assertRaises(KeyError):
            MODULE.trace_delivery(self.delivery)

    def test_missing_label_does_not_silently_drop_image(self):
        (self.delivery / "labels/a.txt").unlink()
        with self.assertRaises(FileNotFoundError):
            MODULE.trace_delivery(self.delivery)

    def test_rejects_label_path_outside_delivery(self):
        self.manifest["a"]["label"] = "../outside.txt"
        self.refresh()
        with self.assertRaisesRegex(ValueError, "escapes delivery"):
            MODULE.trace_delivery(self.delivery)

    def test_rejects_inconsistent_release(self):
        self.put("release.json", '{"release_id":"lab250_wrong"}')
        with self.assertRaisesRegex(ValueError, "release_id"):
            MODULE.trace_delivery(self.delivery)

    def test_ambiguous_changelog_requires_explicit_class(self):
        self.put("guideline/changelog.md", "## v1.3\n- Lớp `car`: đổi\n- Lớp `person`: đổi\n## v1.2\n")
        with self.assertRaisesRegex(ValueError, "Ambiguous"):
            MODULE.trace_delivery(self.delivery)


if __name__ == "__main__":
    unittest.main()
