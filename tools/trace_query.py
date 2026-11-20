"""Trace affected images using only the supplied delivery (Python standard library).

Run from the repository root:
    python tools/trace_query.py runs/r3007/delivery --out runs/r3007/trace.json \
        --evidence runs/r3007/trace_evidence.json

This selects a reinspection scope. It does not confirm annotation errors.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def trace_delivery(delivery, scenes=None, class_name=None, old_guideline=None):
    delivery = Path(delivery).resolve()
    hashes = {}

    def source(relative):
        path = (delivery / relative).resolve()
        if delivery not in path.parents:
            raise ValueError(f"Source escapes delivery: {relative}")
        hashes[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
        return path

    ticket = source("incoming/ticket.md").read_text(encoding="utf-8-sig")
    changelog = source("guideline/changelog.md").read_text(encoding="utf-8-sig")
    classes = {}
    for line in source("classes.txt").read_text(encoding="utf-8-sig").splitlines():
        if line.strip():
            class_id, name = line.split(maxsplit=1)
            classes[name.strip()] = int(class_id)

    scenes = sorted(set(scenes if scenes is not None else re.findall(r"\bscene_\d+\b", ticket)))
    if not scenes:
        raise ValueError("No ticket scenes found; specify --scenes explicitly")
    changed = re.findall(r"^\s*-\s*Lớp\s+`([^`]+)`", changelog, re.MULTILINE)
    if class_name is None:
        if len(set(changed)) != 1:
            raise ValueError("Ambiguous changed class; specify --class-name")
        class_name = changed[0]
    if class_name not in classes:
        raise ValueError(f"Unknown class: {class_name}")
    versions = re.findall(r"^##\s+(v\d+(?:\.\d+)*)\s*$", changelog, re.MULTILINE)
    if old_guideline is None:
        if len(versions) != 2:
            raise ValueError("Expected two guideline versions; specify --old-guideline")
        old_guideline = min(versions, key=lambda v: tuple(map(int, v[1:].split("."))))

    metadata = read_json(source("metadata.json"))["items"]
    with source("jobs.csv").open(encoding="utf-8-sig", newline="") as handle:
        job_rows = list(csv.DictReader(handle))
    jobs = {job["job_id"]: job for job in job_rows}
    if len(jobs) != len(job_rows):
        raise ValueError("Duplicate job_id in jobs.csv")
    manifest = read_json(source("manifest.json"))["items"]
    names = [item["image"] for item in metadata]
    if len(names) != len(set(names)) or set(names) != set(manifest):
        raise ValueError("Metadata image names must be unique and match manifest")
    scene_set = set(scenes)
    absent_scenes = scene_set - {item["scene_id"] for item in metadata}
    if absent_scenes:
        raise ValueError(f"Ticket scenes absent from metadata: {sorted(absent_scenes)}")
    trace = {"tier_a": [], "tier_b": [], "notify": []}
    evidence_rows = []
    affected_jobs = set()
    old_job_images = 0
    mismatches = []
    for item in sorted(metadata, key=lambda row: row["image"]):
        name = item["image"]
        job = jobs[item["job_id"]]
        if item["guideline_version"] != job["guideline"]:
            mismatches.append({"image": name, "job_id": item["job_id"],
                               "image_guideline": item["guideline_version"],
                               "job_guideline": job["guideline"]})
        if job["guideline"] != old_guideline:
            continue
        old_job_images += 1
        label_path = manifest[name]["label"]
        matching_lines = []
        for number, line in enumerate(source(label_path).read_text(encoding="utf-8-sig").splitlines(), 1):
            if not line.strip():
                continue
            columns = line.split()
            if len(columns) != 5:
                raise ValueError(f"Malformed YOLO row at {label_path}:{number}")
            if int(columns[0]) == classes[class_name]:
                matching_lines.append(number)
        if not matching_lines:
            continue
        tier = "tier_a" if item["scene_id"] in scene_set else "tier_b"
        trace[tier].append(name)
        affected_jobs.add(item["job_id"])
        evidence_rows.append({"image": name, "tier": tier, "scene_id": item["scene_id"],
                              "job_id": item["job_id"], "job_guideline": job["guideline"],
                              "image_guideline": item["guideline_version"],
                              "label": label_path, "matching_label_lines": matching_lines,
                              "annotator": job["annotator"], "reviewer": job["reviewer"]})
    trace["notify"] = sorted({jobs[j][role] for j in affected_jobs for role in ("annotator", "reviewer")})
    release = read_json(source("release.json"))
    computed_id = "lab250_" + hashlib.sha256(
        (delivery / "manifest.json").read_bytes() + (delivery / "metadata.json").read_bytes()
    ).hexdigest()[:12]
    if computed_id != release["release_id"]:
        raise ValueError("release_id does not match manifest + metadata")
    evidence = {
        "release_id": computed_id,
        "criteria": {"ticket_scenes": scenes, "class_name": class_name,
                     "class_id": classes[class_name], "old_guideline": old_guideline,
                     "guideline_source": "jobs.csv", "box_source": "labels/ via manifest.json",
                     "meaning": "Scope for reinspection, not confirmed annotation errors"},
        "counts": {"delivery_images": len(metadata), "old_job_images": old_job_images,
                   "tier_a": len(trace["tier_a"]), "tier_b": len(trace["tier_b"]),
                   "notify": len(trace["notify"])},
        "affected_jobs": sorted(affected_jobs),
        "image_job_guideline_mismatches": mismatches,
        "selected_images": evidence_rows,
        "source_sha256": dict(sorted(hashes.items())),
    }
    return trace, evidence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("delivery", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--evidence", type=Path)
    parser.add_argument("--scenes", nargs="+")
    parser.add_argument("--class-name")
    parser.add_argument("--old-guideline")
    args = parser.parse_args()
    delivery = args.delivery.resolve()
    outputs = [p.resolve() for p in (args.out, args.evidence) if p is not None]
    if len(outputs) != len(set(outputs)):
        parser.error("Output and evidence paths must differ")
    if any(path == delivery or delivery in path.parents for path in outputs):
        parser.error("Write outputs outside delivery to preserve v1")
    try:
        trace, evidence = trace_delivery(delivery, args.scenes, args.class_name, args.old_guideline)
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(1, f"Trace failed: {exc}\n")
    for path, payload in ((args.out, trace), (args.evidence, evidence)):
        if path is not None:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(evidence["counts"], ensure_ascii=False))


if __name__ == "__main__":
    main()
