import argparse
import tkinter as tk
from pathlib import Path
from tkinter import messagebox

from PIL import Image, ImageDraw, ImageTk


def load_classes(path):
    classes = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            parts = line.strip().split(maxsplit=1)
            if len(parts) == 2:
                classes[int(parts[0])] = parts[1]
    return classes


def draw_mask_outlines(image, mask_path):
    if not mask_path.exists():
        return image

    mask = Image.open(mask_path).convert("RGB")
    if mask.size != image.size:
        raise ValueError(
            f"Mask size {mask.size} does not match image size {image.size}"
        )

    width, height = mask.size
    src = mask.load()
    overlay = Image.new("RGBA", mask.size, (0, 0, 0, 0))
    dst = overlay.load()
    background = (0, 0, 0)
    outline = (0, 255, 255, 230)

    # Draw boundaries between distinct segment IDs.
    for y in range(height):
        for x in range(width):
            current = src[x, y]
            if current == background:
                continue

            edge = False
            if x + 1 < width and src[x + 1, y] != current:
                edge = True
            if y + 1 < height and src[x, y + 1] != current:
                edge = True

            if edge:
                dst[x, y] = outline

    return Image.alpha_composite(image.convert("RGBA"), overlay)


def draw_yolo_boxes(image, label_path, classes):
    if not label_path.exists():
        return image

    image = image.convert("RGBA")
    draw = ImageDraw.Draw(image)
    width, height = image.size

    for line in label_path.read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if len(parts) < 5:
            continue

        try:
            class_id = int(parts[0])
            cx, cy, bw, bh = map(float, parts[1:5])
        except ValueError:
            continue

        x1 = (cx - bw / 2) * width
        y1 = (cy - bh / 2) * height
        x2 = (cx + bw / 2) * width
        y2 = (cy + bh / 2) * height

        draw.rectangle((x1, y1, x2, y2), outline=(255, 50, 50, 255), width=2)
        name = classes.get(class_id, f"class_{class_id}")
        draw.text((x1 + 2, max(0, y1 - 14)), name, fill=(255, 50, 50, 255))

    return image


class QCViewer:
    def __init__(self, delivery):
        self.delivery = Path(delivery)
        self.images = self.delivery / "images"
        self.labels = self.delivery / "labels"
        self.masks = self.delivery / "masks"
        self.classes = load_classes(self.delivery / "classes.txt")

        if not self.images.is_dir():
            raise FileNotFoundError(f"Images directory not found: {self.images}")

        self.root = tk.Tk()
        self.root.title("Dataset QC Viewer - YOLO + Panoptic")
        self.root.geometry("1150x820")

        top = tk.Frame(self.root)
        top.pack(fill="x", padx=10, pady=8)

        tk.Label(top, text="Image name / ID:").pack(side="left")
        self.entry = tk.Entry(top, width=25)
        self.entry.pack(side="left", padx=6)
        self.entry.insert(0, "000000000139")

        tk.Button(top, text="Open image", command=self.open_image).pack(side="left")
        tk.Button(top, text="Zoom +", command=lambda: self.change_zoom(1.25)).pack(side="left", padx=(8, 0))
        tk.Button(top, text="Zoom -", command=lambda: self.change_zoom(0.8)).pack(side="left")
        tk.Button(top, text="Reset zoom", command=self.reset_zoom).pack(side="left", padx=4)
        self.status = tk.Label(self.root, text="Enter an image ID, then click Open image.")
        self.status.pack(fill="x", padx=10)

        viewer = tk.Frame(self.root)
        viewer.pack(fill="both", expand=True, padx=10, pady=8)
        self.canvas = tk.Canvas(viewer, bg="#222222", width=1100, height=740)
        horizontal = tk.Scrollbar(viewer, orient="horizontal", command=self.canvas.xview)
        vertical = tk.Scrollbar(viewer, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(
            xscrollcommand=horizontal.set,
            yscrollcommand=vertical.set,
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal.grid(row=1, column=0, sticky="ew")
        viewer.grid_rowconfigure(0, weight=1)
        viewer.grid_columnconfigure(0, weight=1)

        self.photo = None
        self.source_image = None
        self.label_exists = False
        self.mask_exists = False
        self.fit_scale = 1.0
        self.zoom = 1.0

        self.root.bind("<Return>", lambda event: self.open_image())
        self.root.bind("<Control-plus>", lambda event: self.change_zoom(1.25))
        self.root.bind("<Control-equal>", lambda event: self.change_zoom(1.25))
        self.root.bind("<Control-minus>", lambda event: self.change_zoom(0.8))
        self.root.bind("<KeyPress-plus>", lambda event: self.change_zoom(1.25))
        self.root.bind("<KeyPress-minus>", lambda event: self.change_zoom(0.8))
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        self.open_image()

    def change_zoom(self, factor):
        if self.source_image is None:
            return
        self.zoom = min(8.0, max(0.25, self.zoom * factor))
        self.render_image()

    def reset_zoom(self):
        if self.source_image is None:
            return
        self.zoom = 1.0
        self.render_image()

    def on_mouse_wheel(self, event):
        self.change_zoom(1.25 if event.delta > 0 else 0.8)
        return "break"

    def render_image(self):
        width = max(1, round(self.source_image.width * self.fit_scale * self.zoom))
        height = max(1, round(self.source_image.height * self.fit_scale * self.zoom))
        image = self.source_image.resize(
            (width, height), Image.Resampling.LANCZOS
        )
        self.photo = ImageTk.PhotoImage(image)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
        self.canvas.configure(scrollregion=(0, 0, width, height))
        self.status.config(
            text=f"{self.current_stem} | Original: "
                 f"{self.source_image.width}x{self.source_image.height} "
                 f"| YOLO: {'OK' if self.label_exists else 'no label'} "
                 f"| Mask: {'OK' if self.mask_exists else 'no mask'} "
                 f"| Zoom: {self.zoom:.2f}x | Red = YOLO, Cyan = segments"
        )

    def open_image(self):
        stem = Path(self.entry.get().strip()).stem
        if not stem:
            return

        image_path = next(
            (self.images / f"{stem}{ext}" for ext in (".jpg", ".jpeg", ".png")
             if (self.images / f"{stem}{ext}").exists()),
            None,
        )

        if image_path is None:
            messagebox.showerror("Image not found", f"Cannot find image: {stem}")
            return

        try:
            image = Image.open(image_path).convert("RGBA")
            mask_path = self.masks / f"{stem}.png"
            label_path = self.labels / f"{stem}.txt"

            image = draw_mask_outlines(image, mask_path)
            image = draw_yolo_boxes(image, label_path, self.classes)

            self.source_image = image
            self.current_stem = stem
            self.label_exists = label_path.exists()
            self.mask_exists = mask_path.exists()
            self.fit_scale = min(1080 / image.width, 700 / image.height, 1.0)
            self.zoom = 1.0
            self.render_image()
        except Exception as exc:
            messagebox.showerror("Viewer error", str(exc))


def main():
    parser = argparse.ArgumentParser(description="View YOLO boxes and panoptic masks.")
    parser.add_argument("delivery", nargs="?", default="runs/r3007/delivery")
    args = parser.parse_args()

    app = QCViewer(args.delivery)
    app.root.mainloop()


if __name__ == "__main__":
    main()
