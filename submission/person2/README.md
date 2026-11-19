# Person 2 - Metadata, Panoptic QC and Image Viewer

- Metadata checks: scene_leak, guideline_mismatch
- Panoptic checks: invalid_category_id, thing_overlap
- Viewer: tools/view_qc.py (YOLO boxes and panoptic segment boundaries)
- Results: clean, r3007, r3008, r3009.

Run viewer: python tools/view_qc.py runs/r3007/delivery
