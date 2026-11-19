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
        ttk.Button(toolbar, text="Open", command=self.open_manual).pack(side="left")
        ttk.Button(toolbar, text="◀ Previous", command=lambda: self.move(-1)).pack(side="left", padx=(14, 3))
        ttk.Button(toolbar, text="Next ▶", command=lambda: self.move(1)).pack(side="left")
        ttk.Button(toolbar, text="Zoom −", command=lambda: self.change_zoom(-1)).pack(side="left", padx=(14, 3))
        ttk.Button(toolbar, text="Zoom +", command=lambda: self.change_zoom(1)).pack(side="left")
        ttk.Button(toolbar, text="Crop candidate", command=self.show_crop).pack(side="left", padx=(14, 3))

        self.status = ttk.Label(self.root, text="Red=YOLO | Cyan=mask edges | Yellow=selected segment/region", padding=(10, 0))
        self.status.pack(fill="x")
        body = ttk.Panedwindow(self.root, orient="horizontal")
        body.pack(fill="both", expand=True, padx=8, pady=8)

        side = ttk.Frame(body, width=340)
        body.add(side, weight=0)
        ttk.Label(side, text=f"Candidates: {len(self.candidates)}", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        list_frame = ttk.Frame(side)
        list_frame.pack(fill="both", expand=True, pady=(6, 10))
        self.listbox = tk.Listbox(list_frame, width=42, exportselection=False)
        self.listbox.pack(side="left", fill="both", expand=True)
        list_scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)
        list_scroll.pack(side="right", fill="y")
        self.listbox.configure(yscrollcommand=list_scroll.set)
        for index, record in enumerate(self.candidates):
            label = f"{index + 1:>3}. {image_stem(record)} | {record.get('type', '?')}"
            self.listbox.insert("end", label)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)
        ttk.Label(side, text="Evidence / reviewer hints:").pack(anchor="w")
        self.details = tk.Text(side, height=15, width=42, wrap="word", state="disabled")
        self.details.pack(fill="x")
        ttk.Label(side, text="Viewer does not write review decisions.\nRecord confirmed/rejected manually with reviewer name.",
                  foreground="#7a4b0a", justify="left").pack(anchor="w", pady=9)

        main = ttk.Frame(body)
        body.add(main, weight=1)
        self.canvas = tk.Canvas(main, bg="#202020", highlightthickness=0)
        self.h_scroll = ttk.Scrollbar(main, orient="horizontal", command=self.canvas.xview)
        self.v_scroll = ttk.Scrollbar(main, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=self.h_scroll.set, yscrollcommand=self.v_scroll.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.v_scroll.grid(row=0, column=1, sticky="ns")
        self.h_scroll.grid(row=1, column=0, sticky="ew")
        main.grid_rowconfigure(0, weight=1)
        main.grid_columnconfigure(0, weight=1)

        self.root.bind("<Return>", lambda _event: self.open_manual())
        self.root.bind("<Right>", lambda _event: self.move(1))
        self.root.bind("<Left>", lambda _event: self.move(-1))
        self.root.bind("<plus>", lambda _event: self.change_zoom(1))
        self.root.bind("<minus>", lambda _event: self.change_zoom(-1))

        if self.candidates:
            self.show_candidate(0)
        else:
            first = next((p.stem for p in sorted(self.images.iterdir())
                          if p.suffix.lower() in (".jpg", ".jpeg", ".png")), None)
            if first:
                self.entry.insert(0, first)
                self.open_manual()
            else:
                self.status.configure(text="No images found")

    def _details(self, value: str):
        self.details.configure(state="normal")
        self.details.delete("1.0", "end")
        self.details.insert("1.0", value)
        self.details.configure(state="disabled")

    def on_select(self, _event):
        selection = self.listbox.curselection()
        if selection and selection[0] != self.current_index:
            self.show_candidate(selection[0])

    def move(self, step: int):
        if self.candidates:
            self.show_candidate(max(0, min(len(self.candidates) - 1, self.current_index + step)))

    def show_candidate(self, index: int):
        if not 0 <= index < len(self.candidates):
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
            image = Image.open(path).convert("RGBA")
            mask_path = self.masks / (stem + ".png")
            selected_sid = candidate.get("segment_id") if candidate else None
            selected_sid = int(selected_sid) if selected_sid is not None else None
            image, segment_rect = mask_overlay(image, mask_path, selected_sid)
            boxes = yolo_boxes(self.labels / (stem + ".txt"), image.width, image.height, self.classes)
            selected_idx = candidate.get("box_index") if candidate else None
            selected_box = next((b for b in boxes if b["index"] == selected_idx), None)
            draw = ImageDraw.Draw(image)
            for box in boxes:
                is_selected = box["index"] == selected_idx
                color = (255, 170, 0, 255) if is_selected else (255, 65, 65, 255)
                draw.rectangle(box["rect"], outline=color, width=4 if is_selected else 2)
                x0, y0 = box["rect"][:2]
                draw.text((x0 + 2, max(0, y0 - 16)), f"#{box['index']} {box['name']}", fill=color)
            self.roi = candidate_roi(candidate, segment_rect, selected_box, image.width, image.height)
            if candidate and self.roi:
                draw.rectangle(self.roi, outline=(255, 230, 0, 255), width=4)
            self.render_base = image
            self.zoom_index = 1
            self.refresh_canvas()
            self.status.configure(text=f"{stem} | {image.width}×{image.height} | "
                                  f"{len(boxes)} boxes | mask={'yes' if mask_path.exists() else 'no'} | "
                                  f"candidate={self.current_index + 1 if candidate else 'manual'}/{len(self.candidates)}")
        except (OSError, ValueError, TypeError) as error:
            messagebox.showerror("Cannot render image", str(error))

    def refresh_canvas(self):
        if self.render_base is None:
            return
        zoom = self.ZOOM_LEVELS[self.zoom_index]
        original = self.render_base
        size = (max(1, round(original.width * zoom)), max(1, round(original.height * zoom)))
        scaled = original.resize(size, Image.Resampling.NEAREST if zoom >= 2 else Image.Resampling.LANCZOS)
        self.photo = ImageTk.PhotoImage(scaled)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
        self.canvas.configure(scrollregion=(0, 0, *size))
        if self.roi:
            self.canvas.update_idletasks()
            center_x = (self.roi[0] + self.roi[2]) / 2 * zoom
            center_y = (self.roi[1] + self.roi[3]) / 2 * zoom
            visible_w = max(1, self.canvas.winfo_width())
            visible_h = max(1, self.canvas.winfo_height())
            self.canvas.xview_moveto(max(0, min(1, (center_x - visible_w / 2) / max(size[0], 1))))
            self.canvas.yview_moveto(max(0, min(1, (center_y - visible_h / 2) / max(size[1], 1))))

    def change_zoom(self, direction: int):
        self.zoom_index = max(0, min(len(self.ZOOM_LEVELS) - 1, self.zoom_index + direction))
        self.refresh_canvas()

    def show_crop(self):
        if self.render_base is None:
            return
        cut = crop_with_margin(self.render_base, self.roi)
        factor = min(4.0, 900 / max(1, cut.width), 680 / max(1, cut.height))
        cut = cut.resize((max(1, round(cut.width * factor)),
                          max(1, round(cut.height * factor))), Image.Resampling.NEAREST)
        window = tk.Toplevel(self.root)
        window.title("Candidate crop — zoomed view")
        photo = ImageTk.PhotoImage(cut)
        label = tk.Label(window, image=photo, bg="#222222")
        label.image = photo
        label.pack(padx=6, pady=6)
        # Keep strong Tk references for any open crop windows.
        self.crop_windows.append(window)
        window.bind("<Destroy>", lambda _event: self._forget_crop(window))

    def _forget_crop(self, window):
        if window in self.crop_windows:
            self.crop_windows.remove(window)


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
