import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
import threading
import os
from src.inpainting import inpaint_auto, inpaint_manual


COLORS = {
    "bg": "#1e1e2e",
    "card": "#2d2d44",
    "primary": "#7c3aed",
    "primary_hover": "#8b5cf6",
    "success": "#10b981",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "text": "#f1f5f9",
    "text_secondary": "#94a3b8",
    "border": "#3d3d5c",
}


class PhotoCleanerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("照片去路人 - Photo Cleaner")
        self.root.geometry("1000x700")
        self.root.configure(bg=COLORS["bg"])

        self.original_image = None
        self.processed_image = None
        self.display_image = None
        self.image_path = None
        self.is_drawing = False
        self.start_x = None
        self.start_y = None
        self.rect_id = None
        self.drawing_mode = False
        self.brush_mode = False
        self.brush_size = 20
        self.draw_mask = None

        self.setup_styles()
        self.setup_ui()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Card.TFrame", background=COLORS["card"])
        style.configure(
            "Title.TLabel",
            background=COLORS["bg"],
            foreground=COLORS["text"],
            font=("Segoe UI", 24, "bold"),
        )
        style.configure(
            "Subtitle.TLabel",
            background=COLORS["bg"],
            foreground=COLORS["text_secondary"],
            font=("Segoe UI", 10),
        )
        style.configure(
            "Status.TLabel",
            background=COLORS["card"],
            foreground=COLORS["text_secondary"],
            font=("Segoe UI", 10),
        )

        style.configure(
            "Primary.TButton",
            background=COLORS["primary"],
            foreground="white",
            font=("Segoe UI", 10, "bold"),
            borderwidth=0,
            padding=(12, 8),
        )
        style.map("Primary.TButton", background=[("active", COLORS["primary_hover"])])

        style.configure(
            "Secondary.TButton",
            background=COLORS["card"],
            foreground=COLORS["text"],
            font=("Segoe UI", 10),
            borderwidth=1,
            bordercolor=COLORS["border"],
            padding=(12, 8),
        )
        style.map("Secondary.TButton", background=[("active", COLORS["border"])])

        style.configure(
            "Toggle.TButton",
            background=COLORS["card"],
            foreground=COLORS["text"],
            borderwidth=0,
            padding=(10, 6),
        )
        style.map("Toggle.TButton", background=[("active", COLORS["primary"])])

    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg=COLORS["bg"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        title_frame = tk.Frame(main_frame, bg=COLORS["bg"])
        title_frame.pack(fill=tk.X, pady=(0, 20))

        title_label = tk.Label(
            title_frame,
            text="照片去路人",
            bg=COLORS["bg"],
            fg=COLORS["text"],
            font=("Segoe UI", 24, "bold"),
        )
        title_label.pack(side=tk.LEFT)

        subtitle_label = tk.Label(
            title_frame,
            text="AI 智能去除照片中的无关人物",
            bg=COLORS["bg"],
            fg=COLORS["text_secondary"],
            font=("Segoe UI", 11),
        )
        subtitle_label.pack(side=tk.LEFT, padx=15, anchor="center")

        toolbar = tk.Frame(main_frame, bg=COLORS["card"], relief="flat", bd=0)
        toolbar.pack(fill=tk.X, pady=(0, 15))
        toolbar.pack_propagate(False)
        toolbar.configure(height=50)

        btn_frame = tk.Frame(toolbar, bg=COLORS["card"])
        btn_frame.pack(side=tk.LEFT, fill=tk.X, padx=10, pady=8)

        self.create_toolbar_button(
            btn_frame, "📂 打开图片", self.load_image, COLORS["primary"]
        ).pack(side=tk.LEFT, padx=5)
        self.create_toolbar_button(
            btn_frame, "✨ 一键去路人", self.auto_remove, COLORS["success"]
        ).pack(side=tk.LEFT, padx=5)
        self.create_toolbar_button(
            btn_frame, "🖌️ 涂抹", self.toggle_brush_mode, COLORS["warning"]
        ).pack(side=tk.LEFT, padx=5)
        self.create_toolbar_button(
            btn_frame, "⬜ 框选", self.toggle_draw_mode, COLORS["text_secondary"]
        ).pack(side=tk.LEFT, padx=5)
        self.create_toolbar_button(
            btn_frame, "💾 保存图片", self.save_image, COLORS["primary"]
        ).pack(side=tk.LEFT, padx=5)
        self.create_toolbar_button(
            btn_frame, "🔄 重置", self.reset, COLORS["text_secondary"]
        ).pack(side=tk.LEFT, padx=5)

        self.mode_label = tk.Label(
            toolbar,
            text="浏览模式",
            bg=COLORS["card"],
            fg=COLORS["text_secondary"],
            font=("Segoe UI", 10),
        )
        self.mode_label.pack(side=tk.RIGHT, padx=15)

        canvas_container = tk.Frame(main_frame, bg=COLORS["card"], relief="flat", bd=0)
        canvas_container.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(
            canvas_container,
            bg="#1a1a2e",
            highlightthickness=0,
            cursor="crosshair",
        )
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)

        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)

        status_frame = tk.Frame(main_frame, bg=COLORS["card"], relief="flat", bd=0)
        status_frame.pack(fill=tk.X, pady=(15, 0))
        status_frame.configure(height=40)

        self.status_label = tk.Label(
            status_frame,
            text="欢迎使用！请打开图片开始处理",
            bg=COLORS["card"],
            fg=COLORS["text_secondary"],
            font=("Segoe UI", 10),
        )
        self.status_label.pack(side=tk.LEFT, padx=15, pady=10)

        self.progress = ttk.Progressbar(status_frame, mode="indeterminate", length=150)
        self.progress.pack(side=tk.RIGHT, padx=15, pady=10)

    def create_toolbar_button(self, parent, text, command, color):
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=color,
            fg="white" if color != COLORS["text_secondary"] else COLORS["text"],
            font=(
                "Segoe UI",
                10,
                "bold" if color != COLORS["text_secondary"] else "normal",
            ),
            relief="flat",
            bd=0,
            padx=15,
            pady=8,
            cursor="hand2",
            activebackground=self.lighten_color(color),
            activeforeground="white",
        )
        return btn

    def lighten_color(self, hex_color):
        if hex_color == COLORS["text_secondary"]:
            return COLORS["border"]
        return hex_color

    def load_image(self):
        file_path = filedialog.askopenfilename(
            title="选择图片",
            filetypes=[
                ("图片文件", "*.jpg *.jpeg *.png *.bmp *.webp"),
                ("所有文件", "*.*"),
            ],
        )
        if file_path:
            self.image_path = file_path
            ext = os.path.splitext(file_path)[1].lower()
            valid_exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".gif"}
            if ext not in valid_exts:
                messagebox.showerror(
                    "错误",
                    f"不支持的图片格式: {ext}\n请选择 JPG、PNG、BMP、WEBP 或 GIF 格式的图片",
                )
                return
            if not os.path.exists(file_path):
                messagebox.showerror("错误", f"文件不存在: {file_path}")
                return
            try:
                pil_img = Image.open(file_path)
                pil_img = pil_img.convert("RGB")
                self.original_image = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
                self.processed_image = self.original_image.copy()
                self.display_image_on_canvas(self.original_image)
                filename = os.path.basename(file_path)
                self.status_label.config(
                    text=f"已加载: {filename}", fg=COLORS["success"]
                )
            except Exception as e:
                messagebox.showerror("错误", f"读取图片失败: {str(e)}")

    def display_image_on_canvas(self, image):
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w = image_rgb.shape[:2]

        canvas_width = self.canvas.winfo_width() or 800
        canvas_height = self.canvas.winfo_height() or 500

        scale = min(canvas_width / w, canvas_height / h, 1)
        new_w = int(w * scale)
        new_h = int(h * scale)

        image_resized = cv2.resize(image_rgb, (new_w, new_h))

        self.display_image = ImageTk.PhotoImage(Image.fromarray(image_resized))

        self.canvas.delete("all")
        self.canvas.create_image(
            new_w // 2, new_h // 2, image=self.display_image, anchor=tk.CENTER
        )

        self.canvas.config(width=new_w, height=new_h)

    def auto_remove(self):
        if self.original_image is None:
            messagebox.showwarning("警告", "请先打开图片")
            return

        self.status_label.config(text="正在智能识别并去除路人...", fg=COLORS["warning"])
        self.progress.start(10)
        self.root.update()

        def process():
            try:
                result, mask = inpaint_auto(self.original_image)
                self.processed_image = result
                self.root.after(0, self.display_result, result)
            except Exception as e:
                import traceback

                with open("debug.log", "a", encoding="utf-8") as f:
                    f.write(f"[DEBUG] 错误: {e}\n{traceback.format_exc()}\n")
                self.root.after(0, messagebox.showerror, "错误", f"处理失败: {str(e)}")

        thread = threading.Thread(target=process)
        thread.start()

    def display_result(self, image):
        self.display_image_on_canvas(image)
        self.root.update()
        self.progress.stop()
        self.status_label.config(
            text="处理完成！可预览或保存结果", fg=COLORS["success"]
        )

    def toggle_draw_mode(self):
        if self.original_image is None:
            messagebox.showwarning("警告", "请先打开图片")
            return

        self.drawing_mode = not self.drawing_mode
        if self.drawing_mode:
            self.brush_mode = False
            self.mode_label.config(text="框选模式", fg=COLORS["warning"])
            self.canvas.config(cursor="crosshair")
        else:
            self.mode_label.config(text="浏览模式", fg=COLORS["text_secondary"])
            self.canvas.config(cursor="crosshair")

    def toggle_brush_mode(self):
        if self.original_image is None:
            messagebox.showwarning("警告", "请先打开图片")
            return

        self.brush_mode = not self.brush_mode
        if self.brush_mode:
            self.drawing_mode = False
            h, w = self.original_image.shape[:2]
            self.draw_mask = np.zeros((h, w), dtype=np.uint8)
            self.mode_label.config(text="涂抹中...点击完成", fg=COLORS["danger"])
            self.canvas.config(cursor="pencil")
        else:
            self.apply_brush_mask()
            self.mode_label.config(text="浏览模式", fg=COLORS["text_secondary"])
            self.canvas.config(cursor="crosshair")

    def apply_brush_mask(self):
        if self.draw_mask is None or self.original_image is None:
            return

        pixels = cv2.countNonZero(self.draw_mask)
        with open("debug.log", "a", encoding="utf-8") as f:
            f.write(f"[BRUSH] 涂抹像素: {pixels}\n")

        if pixels > 0:
            self.status_label.config(text="正在处理涂抹区域...", fg=COLORS["warning"])
            self.progress.start(10)
            self.root.update()

            def process():
                try:
                    result = cv2.inpaint(
                        self.original_image, self.draw_mask, 3, cv2.INPAINT_TELEA
                    )
                    diff = cv2.absdiff(result, self.original_image)
                    diff_sum = cv2.sumElems(diff)[0]
                    with open("debug.log", "a", encoding="utf-8") as f:
                        f.write(f"[BRUSH] 处理完成, 差异: {diff_sum}\n")
                    self.processed_image = result
                    self.draw_mask = None
                    self.root.after(0, self.display_result, result)
                except Exception as e:
                    import traceback

                    with open("debug.log", "a", encoding="utf-8") as f:
                        f.write(f"[BRUSH] 错误: {e}\n{traceback.format_exc()}\n")
                    self.root.after(
                        0, messagebox.showerror, "错误", f"处理失败: {str(e)}"
                    )

            thread = threading.Thread(target=process)
            thread.start()

    def on_mouse_down(self, event):
        if self.brush_mode:
            self.is_drawing = True
            self.draw_at_position(event.x, event.y)
        elif self.drawing_mode:
            self.is_drawing = True
            self.start_x = event.x
            self.start_y = event.y
        else:
            return

    def draw_at_position(self, x, y):
        if self.draw_mask is None or self.original_image is None:
            return

        h, w = self.original_image.shape[:2]
        canvas_width = self.canvas.winfo_width() or 1
        canvas_height = self.canvas.winfo_height() or 1
        scale = min(canvas_width / w, canvas_height / h, 1)

        ix = int(x / scale)
        iy = int(y / scale)

        cv2.circle(self.draw_mask, (ix, iy), self.brush_size, 255, -1)

        self.display_with_mask()

    def display_with_mask(self):
        if self.original_image is None:
            return

        image_rgb = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
        h, w = image_rgb.shape[:2]

        canvas_width = self.canvas.winfo_width() or 800
        canvas_height = self.canvas.winfo_height() or 500
        scale = min(canvas_width / w, canvas_height / h, 1)
        new_w = int(w * scale)
        new_h = int(h * scale)

        image_resized = cv2.resize(image_rgb, (new_w, new_h))

        if self.draw_mask is not None:
            mask_resized = cv2.resize(self.draw_mask, (new_w, new_h))
            mask_colored = cv2.applyColorMap(mask_resized, cv2.COLORMAP_JET)
            mask_rgb = cv2.cvtColor(mask_colored, cv2.COLOR_BGR2RGB)
            overlay = cv2.addWeighted(image_resized, 0.7, mask_rgb, 0.3, 0)
            self.display_image = ImageTk.PhotoImage(Image.fromarray(overlay))
        else:
            self.display_image = ImageTk.PhotoImage(Image.fromarray(image_resized))

        self.canvas.delete("all")
        self.canvas.create_image(
            new_w // 2, new_h // 2, image=self.display_image, anchor=tk.CENTER
        )

    def on_mouse_move(self, event):
        if self.brush_mode and self.is_drawing:
            self.draw_at_position(event.x, event.y)
        elif self.drawing_mode and self.is_drawing:
            if self.rect_id:
                self.canvas.delete(self.rect_id)

            start_x = float(self.start_x) if self.start_x is not None else 0
            start_y = float(self.start_y) if self.start_y is not None else 0
            self.rect_id = self.canvas.create_rectangle(
                start_x,
                start_y,
                float(event.x),
                float(event.y),
                outline="#f59e0b",
                width=3,
            )

    def on_mouse_up(self, event):
        if self.brush_mode:
            self.is_drawing = False
            self.apply_brush_mask()
        elif self.drawing_mode and self.is_drawing:
            self.is_drawing = False

            if self.rect_id:
                self.canvas.delete(self.rect_id)
                self.rect_id = None

            if self.original_image is None:
                return

            self.status_label.config(text="正在处理选中区域...", fg=COLORS["warning"])
            self.progress.start(10)
            self.root.update()

            h, w = self.original_image.shape[:2]
            canvas_width = self.canvas.winfo_width() or 1
            canvas_height = self.canvas.winfo_height() or 1
            scale = min(canvas_width / w, canvas_height / h, 1)

            start_x = self.start_x if self.start_x is not None else 0
            start_y = self.start_y if self.start_y is not None else 0
            x1 = int(start_x / scale)
            y1 = int(start_y / scale)
            x2 = int(event.x / scale)
            y2 = int(event.y / scale)

            def process():
                try:
                    result, mask = inpaint_manual(self.original_image, x1, y1, x2, y2)
                    self.processed_image = result
                    self.root.after(0, self.display_result, result)
                except Exception as e:
                    self.root.after(
                        0, messagebox.showerror, "错误", f"处理失败: {str(e)}"
                    )

            thread = threading.Thread(target=process)
            thread.start()

    def save_image(self):
        if self.processed_image is None:
            messagebox.showwarning("警告", "没有可保存的图片")
            return

        file_path = filedialog.asksaveasfilename(
            title="保存图片",
            defaultextension=".jpg",
            filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png"), ("BMP", "*.bmp")],
        )

        if file_path:
            cv2.imwrite(file_path, self.processed_image)
            self.status_label.config(
                text=f"已保存: {os.path.basename(file_path)}", fg=COLORS["success"]
            )
            messagebox.showinfo("成功", "图片已保存")

    def reset(self):
        if self.original_image is not None:
            self.processed_image = self.original_image.copy()
            self.display_image_on_canvas(self.original_image)
            self.status_label.config(text="已重置", fg=COLORS["success"])


def run():
    root = tk.Tk()
    app = PhotoCleanerApp(root)
    root.mainloop()


if __name__ == "__main__":
    run()
