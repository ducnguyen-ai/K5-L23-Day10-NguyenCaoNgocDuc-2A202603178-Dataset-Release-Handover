"""YOLO + panoptic candidate viewer for Day 10 (Person 2/3 handoff).

Usage from the repository root (requires Pillow):
    python -X utf8 tools/view_qc.py runs/r3007/delivery \
        --candidates runs/r3007/candidates_p3.json

This program only VISUALIZES candidates. It does not confirm/reject errors or
write review_log.csv; the team must inspect images and record decisions itself.
"""

from __future__ import annotations

import argparse
import json
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from PIL import Image, ImageDraw, ImageTk


def load_classes(path: Path) -> dict[int, str]:
    classes = {}
    if path.is_file():
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            parts = line.strip().split(maxsplit=1)
            if len(parts) == 2:
                classes[int(parts[0])] = parts[1]
    return classes


def load_candidates(path: Path | None) -> list[dict]:
    if path is None:
        return []
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    status = payload.get("status")
    if status != "generated_for_human_review":
        raise ValueError(f"Not a generated review queue: status={status!r}")
    records = payload.get("candidates")
    if not isinstance(records, list):
        raise ValueError("candidates must be a list")
    for index, record in enumerate(records):
        if not isinstance(record, dict) or not (record.get("image") or record.get("target")):
            raise ValueError(f"Invalid candidate at index {index}")
    return records


def image_stem(record: dict) -> str:
    name = str(record.get("image") or record.get("target") or "").strip()
    return Path(name).stem


def image_file(images_dir: Path, stem: str) -> Path | None:
    # Only a plain stem is accepted. Candidates cannot point outside images/.
    if not stem or Path(stem).name != stem or stem in (".", ".."):
        return None
    for suffix in (".jpg", ".jpeg", ".png", ".JPG", ".JPEG"):
        path = images_dir / (stem + suffix)
        if path.is_file():
            return path
    return None


def yolo_boxes(label_path: Path, width: int, height: int, classes: dict[int, str]):
    if not label_path.is_file():
        return []
    boxes = []
    for line_idx, line in enumerate(label_path.read_text(encoding="utf-8-sig").splitlines()):
        parts = line.split()
        if len(parts) != 5:
            continue
        try:
            cls = int(parts[0])
            cx, cy, bw, bh = map(float, parts[1:])
            values = ((cx - bw / 2) * width, (cy - bh / 2) * height,
                      (cx + bw / 2) * width, (cy + bh / 2) * height)
            if not all(float("-inf") < x < float("inf") for x in values):
                continue
        except ValueError:
            continue
        if values[2] <= values[0] or values[3] <= values[1]:
            continue
        boxes.append({"index": line_idx, "name": classes.get(cls, f"class_{cls}"),
                      "rect": values})
    return boxes


def segment_rgb(sid: int) -> tuple[int, int, int]:
    return sid & 255, (sid >> 8) & 255, (sid >> 16) & 255


def mask_overlay(image: Image.Image, path: Path, selected_sid: int | None):
    """Render all segment edges cyan, and selected segment with yellow fill."""
    if not path.is_file():
        return image, None
    mask = Image.open(path).convert("RGB")
    if mask.size != image.size:
        raise ValueError(f"Mask {mask.size} differs from image {image.size}: {path.name}")
    width, height = mask.size
    data = mask.load()
    layer = Image.new("RGBA", mask.size, (0, 0, 0, 0))
    target = segment_rgb(selected_sid) if selected_sid is not None else None
    layer_pixels = layer.load()
    x0, y0, x1, y1 = width, height, -1, -1
    for y in range(height):
        for x in range(width):
            current = data[x, y]
            chosen = target is not None and current == target
            if chosen:
                x0, y0 = min(x0, x), min(y0, y)
                x1, y1 = max(x1, x), max(y1, y)
            if current == (0, 0, 0):
                continue
            edge = ((x == 0 or data[x - 1, y] != current)
                    or (x + 1 == width or data[x + 1, y] != current)
                    or (y == 0 or data[x, y - 1] != current)
                    or (y + 1 == height or data[x, y + 1] != current))
            if edge:
                layer_pixels[x, y] = (255, 210, 0, 255) if chosen else (0, 255, 255, 225)
            elif chosen:
                layer_pixels[x, y] = (255, 210, 0, 70)
    region = (x0, y0, x1 + 1, y1 + 1) if x1 >= x0 else None
    return Image.alpha_composite(image, layer), region


def candidate_roi(candidate: dict | None, segment_rect, selected_box, width: int, height: int):
    location = candidate.get("location") if candidate else None
    if isinstance(location, (list, tuple)) and len(location) == 4:
        try:
            x0, y0, x1, y1 = [float(v) for v in location]
            if x1 > x0 and y1 > y0:
                return (max(0, x0), max(0, y0), min(width, x1), min(height, y1))
        except (ValueError, TypeError):
            pass
    if segment_rect:
        return segment_rect
    return selected_box["rect"] if selected_box else None


def crop_with_margin(image: Image.Image, region, margin_fraction=0.30):
    if not region:
        return image.copy()
    x0, y0, x1, y1 = region
    pad = max(16, int(max(x1 - x0, y1 - y0) * margin_fraction))
    bounds = (max(0, int(x0) - pad), max(0, int(y0) - pad),
              min(image.width, int(x1) + pad), min(image.height, int(y1) + pad))
    return image.crop(bounds)


class QCViewer:
    ZOOM_LEVELS = (0.5, 1.0, 1.5, 2.0, 3.0, 4.0)

    def __init__(self, delivery: Path, candidates_path: Path | None = None):
        self.delivery = Path(delivery).resolve(strict=True)
        self.images = self.delivery / "images"
        self.labels = self.delivery / "labels"
        self.masks = self.delivery / "masks"
        self.classes = load_classes(self.delivery / "classes.txt")
        if not self.images.is_dir():
            raise FileNotFoundError(f"Missing images directory: {self.images}")
        self.candidates = load_candidates(candidates_path)
        self.current_index = -1
        self.zoom_index = 1
        self.render_base = None
        self.roi = None
        self.photo = None
        self.crop_windows = []

        self.root = tk.Tk()
        self.root.title("Day10 QC Viewer — YOLO + Panoptic + Candidates")
        self.root.geometry("1450x890")

        toolbar = ttk.Frame(self.root, padding=8)
        toolbar.pack(fill="x")
        ttk.Label(toolbar, text="Image stem:").pack(side="left")
        self.entry = ttk.Entry(toolbar, width=23)
        self.entry.pack(side="left", padx=6)
        self.entry.insert(0, "000000000139")

        tk.Button(top, text="Open image", command=self.open_image).pack(side="left")
        self.status = tk.Label(self.root, text="Enter an image ID, then click Open image.")
        self.status.pack(fill="x", padx=10)

        self.canvas = tk.Canvas(self.root, bg="#222222", width=1100, height=740)
        self.canvas.pack(fill="both", expand=True, padx=10, pady=8)
        self.photo = None

        self.root.bind("<Return>", lambda event: self.open_image())
        self.open_image()

    def open_image(self):
        stem = Path(self.entry.get().strip()).stem
        if not stem:
            return
        self.current_index = index
        self.listbox.selection_clear(0, "end")
        self.listbox.selection_set(index)
        self.listbox.see(index)
        record = self.candidates[index]
        stem = image_stem(record)
        self.entry.delete(0, "end")
        self.entry.insert(0, stem)
        possible = record.get("possible_types") or []
        hint = "\nReview must decide: " + " OR ".join(possible) if possible else ""
        self._details(f"Candidate {index + 1}/{len(self.candidates)}\n\n"
                      + json.dumps(record, ensure_ascii=False, indent=2) + hint)
        self.render(stem, record)

    def open_manual(self):
        self.current_index = -1
        self.listbox.selection_clear(0, "end")
        self._details("Manual image mode. Select a candidate to show its evidence.")
        self.render(Path(self.entry.get().strip()).stem, None)

    def render(self, stem: str, candidate: dict | None):
        path = image_file(self.images, stem)
        if path is None:
            messagebox.showerror("Image missing", f"Image not found inside delivery/images: {stem}")
            return
        try:
            image = Image.open(image_path).convert("RGBA")
            mask_path = self.masks / f"{stem}.png"
            label_path = self.labels / f"{stem}.txt"

            image = draw_mask_outlines(image, mask_path)
            image = draw_yolo_boxes(image, label_path, self.classes)

            original_size = image.size
            image.thumbnail((1080, 700), Image.Resampling.LANCZOS)

            self.photo = ImageTk.PhotoImage(image)
            self.canvas.delete("all")
            self.canvas.create_image(10, 10, anchor="nw", image=self.photo)
            self.canvas.configure(
                scrollregion=(0, 0, image.width + 20, image.height + 20)
            )

            self.status.config(
                text=f"{stem} | Original: {original_size[0]}x{original_size[1]} "
                     f"| YOLO: {'OK' if label_path.exists() else 'no label'} "
                     f"| Mask: {'OK' if mask_path.exists() else 'no mask'} "
                     f"| Red = YOLO boxes | Cyan = segment boundaries"
            )
        except Exception as exc:
            messagebox.showerror("Viewer error", str(exc))


def main():
    parser = argparse.ArgumentParser(description="Inspect YOLO boxes, panoptic masks, and review candidates")
    parser.add_argument("delivery", nargs="?", type=Path, default=Path("runs/r3007/delivery"))
    parser.add_argument("--candidates", type=Path, help="Generated candidates.json with review status")
    args = parser.parse_args()
    try:
        viewer = QCViewer(args.delivery, args.candidates)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    viewer.root.mainloop()


if __name__ == "__main__":
    main()
