import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageEnhance
import cv2
import numpy as np
import time


class SketchArtApp:

    def __init__(self, root):

        self.root = root
        self.root.title("Image To Sketch Art")
        self.root.geometry("1500x820")
        self.root.configure(bg="#d9d9d9")

        # =========================
        # VARIABLES
        # =========================

        self.original_image = None
        self.sketch_image = None

        self.original_display = None
        self.sketch_display = None

        self.undo_stack = []

        self.zoom_original = 1.0
        self.zoom_sketch = 1.0

        self.drag_x = 0
        self.drag_y = 0

        # =========================
        # TITLE
        # =========================

        title = tk.Label(
            root,
            text="IMAGE TO SKETCH ART",
            font=("Arial", 28, "bold"),
            bg="#d9d9d9"
        )

        title.pack(pady=15)

        # =========================
        # BUTTON FRAME
        # =========================

        self.button_frame = tk.Frame(
            root,
            bg="#d9d9d9"
        )

        self.button_frame.pack(pady=10)

        # =========================
        # BUTTON STYLE
        # =========================

        button_style = {
            "width": 14,
            "height": 2,
            "font": ("Arial", 11, "bold"),
            "bd": 3,
            "cursor": "hand2"
        }

        # =========================
        # BUTTONS
        # =========================

        buttons = [

            ("Upload Image", self.upload_image,
             "#ff7f50", "white"),

            ("Pencil Art", self.convert_to_sketch,
             "#3cb371", "white"),

            ("Dark Sketch", self.convert_to_dark_sketch,
             "#708090", "white"),

            ("Vintage Filter", self.apply_vintage_filter,
             "#800080", "white"),

            ("Grayscale", self.apply_grayscale,
             "#808080", "white"),

            ("Undo", self.undo_action,
             "#87cefa", "black"),

            ("Clear", self.clear_image,
             "#ff6347", "white")

        ]

        for text, command, bg, fg in buttons:

            btn = tk.Button(
                self.button_frame,
                text=text,
                command=command,
                bg=bg,
                fg=fg,
                **button_style
            )

            btn.pack(
                side=tk.LEFT,
                padx=8
            )

        # =========================
        # MAIN FRAME
        # =========================

        self.main_frame = tk.Frame(
            root,
            bg="#d9d9d9"
        )

        self.main_frame.pack(pady=20)

        # =========================
        # LEFT FRAME
        # =========================

        self.left_frame = tk.Frame(
            self.main_frame,
            bg="#d9d9d9"
        )

        self.left_frame.grid(
            row=0,
            column=0,
            padx=20
        )

        tk.Label(
            self.left_frame,
            text="Original Image",
            font=("Arial", 16, "bold"),
            bg="#d9d9d9"
        ).pack(pady=10)

        self.canvas_original = tk.Canvas(
            self.left_frame,
            width=550,
            height=500,
            bg="#add8e6",
            highlightbackground="black",
            highlightthickness=3
        )

        self.canvas_original.pack()

        # =========================
        # CENTER FRAME
        # =========================

        self.center_frame = tk.Frame(
            self.main_frame,
            bg="#d9d9d9"
        )

        self.center_frame.grid(
            row=0,
            column=1,
            padx=25
        )

        # =========================
        # SAVE BUTTON
        # =========================

        save_btn = tk.Button(
            self.center_frame,
            text="Save Image",
            command=self.save_image,
            bg="#1e90ff",
            fg="white",
            width=14,
            height=1,
            font=("Arial", 12, "bold"),
            bd=3,
            cursor="hand2"
        )

        save_btn.pack(pady=20)

        # =========================
        # BRIGHTNESS SLIDER
        # =========================

        tk.Label(
            self.center_frame,
            text="Brightness",
            font=("Arial", 13, "bold"),
            bg="#d9d9d9"
        ).pack(pady=(10, 5))

        self.brightness_slider = tk.Scale(
            self.center_frame,
            from_=0.5,
            to=2.0,
            resolution=0.1,
            orient="horizontal",
            length=220,
            sliderlength=25,
            bg="#d9d9d9",
            font=("Arial", 10),
            command=self.apply_brightness_slider
        )

        self.brightness_slider.set(1.0)

        self.brightness_slider.pack(pady=10)

        # =========================
        # ORIGINAL ZOOM
        # =========================

        tk.Label(
            self.center_frame,
            text="Original Zoom",
            font=("Arial", 13, "bold"),
            bg="#d9d9d9"
        ).pack(pady=(20, 5))

        tk.Button(
            self.center_frame,
            text="Zoom In +",
            command=self.zoom_in_original,
            bg="#90ee90",
            width=12,
            font=("Arial", 11, "bold")
        ).pack(pady=5)

        tk.Button(
            self.center_frame,
            text="Zoom Out -",
            command=self.zoom_out_original,
            bg="#ffb6c1",
            width=12,
            font=("Arial", 11, "bold")
        ).pack(pady=5)

        # =========================
        # EDITED ZOOM
        # =========================

        tk.Label(
            self.center_frame,
            text="Edited Zoom",
            font=("Arial", 13, "bold"),
            bg="#d9d9d9"
        ).pack(pady=(25, 5))

        tk.Button(
            self.center_frame,
            text="Zoom In +",
            command=self.zoom_in_sketch,
            bg="#90ee90",
            width=12,
            font=("Arial", 11, "bold")
        ).pack(pady=5)

        tk.Button(
            self.center_frame,
            text="Zoom Out -",
            command=self.zoom_out_sketch,
            bg="#ffb6c1",
            width=12,
            font=("Arial", 11, "bold")
        ).pack(pady=5)

        # =========================
        # RIGHT FRAME
        # =========================

        self.right_frame = tk.Frame(
            self.main_frame,
            bg="#d9d9d9"
        )

        self.right_frame.grid(
            row=0,
            column=2,
            padx=20
        )

        tk.Label(
            self.right_frame,
            text="Edited Image",
            font=("Arial", 16, "bold"),
            bg="#d9d9d9"
        ).pack(pady=10)

        self.canvas_sketch = tk.Canvas(
            self.right_frame,
            width=550,
            height=500,
            bg="#f5f5dc",
            highlightbackground="black",
            highlightthickness=3
        )

        self.canvas_sketch.pack()

        # =========================
        # PROGRESS BAR
        # =========================

        self.progress = ttk.Progressbar(
            root,
            orient="horizontal",
            length=1200,
            mode="determinate"
        )

        self.progress.pack(pady=15)

    # =========================
    # DISPLAY IMAGE
    # =========================

    def display_image(self, image, canvas, side):

        if image is None:
            return

        img = image.copy()

        zoom = self.zoom_original if side == "original" else self.zoom_sketch

        canvas_width = 550
        canvas_height = 450

        ratio = min(
            canvas_width / img.width,
            canvas_height / img.height
        )

        width = int(img.width * ratio * zoom)
        height = int(img.height * ratio * zoom)

        img = img.resize((width, height), Image.LANCZOS)

        tk_img = ImageTk.PhotoImage(img)

        canvas.delete("all")

        canvas.create_image(
            canvas_width // 2,
            canvas_height // 2,
            image=tk_img
        )

        if side == "original":
            self.original_display = tk_img
        else:
            self.sketch_display = tk_img

    # =========================
    # UPLOAD IMAGE
    # =========================

    def upload_image(self):

        path = filedialog.askopenfilename(
            filetypes=[
                ("Images", "*.jpg *.jpeg *.png *.bmp")
            ]
        )

        if not path:
            return

        self.original_image = Image.open(path).convert("RGB")

        self.sketch_image = self.original_image.copy()

        self.zoom_original = 1.0
        self.zoom_sketch = 1.0

        self.display_image(
            self.original_image,
            self.canvas_original,
            "original"
        )

        self.display_image(
            self.sketch_image,
            self.canvas_sketch,
            "sketch"
        )

    # =========================
    # PROGRESS EFFECT
    # =========================

    def processing_effect(self):

        self.progress["value"] = 0

        for i in range(101):

            self.progress["value"] = i

            self.root.update_idletasks()

            time.sleep(0.01)

    # =========================
    # SAVE STATE
    # =========================

    def save_state(self):

        if self.sketch_image:
            self.undo_stack.append(
                self.sketch_image.copy()
            )

    # =========================
    # PENCIL ART
    # =========================

    def convert_to_sketch(self):

        if self.sketch_image is None:
            return

        self.save_state()

        self.processing_effect()

        img = np.array(self.sketch_image)

        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

        invert = 255 - gray

        blur = cv2.GaussianBlur(invert, (21, 21), 0)

        inverted = 255 - blur

        sketch = cv2.divide(gray, inverted, scale=256.0)

        self.sketch_image = Image.fromarray(sketch).convert("RGB")

        self.display_image(
            self.sketch_image,
            self.canvas_sketch,
            "sketch"
        )

    # =========================
    # DARK SKETCH
    # =========================

    def convert_to_dark_sketch(self):

        if self.sketch_image is None:
            return

        self.save_state()

        self.processing_effect()

        img = np.array(self.sketch_image)

        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

        invert = 255 - gray

        blur = cv2.GaussianBlur(invert, (31, 31), 0)

        inverted_blur = 255 - blur

        sketch = cv2.divide(gray, inverted_blur, scale=256.0)

        dark_sketch = cv2.multiply(sketch, np.array([0.7]))

        dark_sketch = cv2.convertScaleAbs(
            dark_sketch,
            alpha=1.4,
            beta=-20
        )

        self.sketch_image = Image.fromarray(
            dark_sketch
        ).convert("RGB")

        self.display_image(
            self.sketch_image,
            self.canvas_sketch,
            "sketch"
        )

    # =========================
    # VINTAGE FILTER
    # =========================

    def apply_vintage_filter(self):

        if self.sketch_image is None:
            return

        self.save_state()

        self.processing_effect()

        img = self.sketch_image.copy()

        r, g, b = img.split()

        r = r.point(lambda i: i * 1.2)

        b = b.point(lambda i: i * 0.8)

        self.sketch_image = Image.merge("RGB", (r, g, b))

        self.display_image(
            self.sketch_image,
            self.canvas_sketch,
            "sketch"
        )

    # =========================
    # GRAYSCALE
    # =========================

    def apply_grayscale(self):

        if self.sketch_image is None:
            return

        self.save_state()

        self.processing_effect()

        gray = self.sketch_image.convert("L")

        self.sketch_image = gray.convert("RGB")

        self.display_image(
            self.sketch_image,
            self.canvas_sketch,
            "sketch"
        )

    # =========================
    # BRIGHTNESS
    # =========================

    def apply_brightness_slider(self, value):

        if self.original_image is None:
            return

        enhancer = ImageEnhance.Brightness(
            self.original_image
        )

        bright = enhancer.enhance(float(value))

        self.sketch_image = bright

        self.display_image(
            self.sketch_image,
            self.canvas_sketch,
            "sketch"
        )

    # =========================
    # UNDO
    # =========================

    def undo_action(self):

        if len(self.undo_stack) == 0:
            return

        self.sketch_image = self.undo_stack.pop()

        self.display_image(
            self.sketch_image,
            self.canvas_sketch,
            "sketch"
        )

    # =========================
    # CLEAR
    # =========================

    def clear_image(self):

        self.canvas_original.delete("all")

        self.canvas_sketch.delete("all")

        self.original_image = None

        self.sketch_image = None

        self.undo_stack.clear()

    # =========================
    # SAVE IMAGE
    # =========================

    def save_image(self):

        if self.sketch_image is None:
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG", "*.png"),
                ("JPEG", "*.jpg")
            ]
        )

        if path:

            self.sketch_image.save(path)

            messagebox.showinfo(
                "Saved",
                "Image Saved Successfully"
            )

    # =========================
    # ZOOM
    # =========================

    def zoom_in_original(self):

        self.zoom_original += 0.1

        self.display_image(
            self.original_image,
            self.canvas_original,
            "original"
        )

    def zoom_out_original(self):

        self.zoom_original -= 0.1

        if self.zoom_original < 0.2:
            self.zoom_original = 0.2

        self.display_image(
            self.original_image,
            self.canvas_original,
            "original"
        )

    def zoom_in_sketch(self):

        self.zoom_sketch += 0.1

        self.display_image(
            self.sketch_image,
            self.canvas_sketch,
            "sketch"
        )

    def zoom_out_sketch(self):

        self.zoom_sketch -= 0.1

        if self.zoom_sketch < 0.2:
            self.zoom_sketch = 0.2

        self.display_image(
            self.sketch_image,
            self.canvas_sketch,
            "sketch"
        )


if __name__ == "__main__":

    root = tk.Tk()

    app = SketchArtApp(root)

    root.mainloop()