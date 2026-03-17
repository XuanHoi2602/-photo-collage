import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel, Scrollbar
from PIL import Image, ImageTk, ImageGrab
import os
import webbrowser
import ctypes
import sys

def resource_path(relative_path):
    """ Lấy đường dẫn tuyệt đối đến tài nguyên """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

ICON_APP_PATH  = resource_path("app_icon.ico")
ICON_FB_PATH   = resource_path(os.path.join("assets", "fb.png"))
ICON_VPS_PATH  = resource_path(os.path.join("assets", "vps.png"))
ICON_ZALO_PATH = resource_path(os.path.join("assets", "zalo.png"))

# --- CẤU HÌNH ---
TARGET_CANVAS_WIDTH = 2000  
ROW_BASE_HEIGHT = 800

LINK_FACEBOOK = "https://www.facebook.com/nguyenxuanhoidz/"
LINK_VPS      = "https://portal.vpsgame.net/" 
LINK_ZALO     = "https://zalo.me/g/hahaae860" 

class AutoArrangePreviewApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ghép ảnh Pro - By Darrk")
        
        # --- THIẾT LẬP KÍCH THƯỚC ---
        self.root.geometry("1200x700") 
        self.root.minsize(900, 700) 
        
        # --- SET ICON ---
        try:
            if os.path.exists(ICON_APP_PATH):
                self.root.iconbitmap(ICON_APP_PATH)
                img_icon = Image.open(ICON_APP_PATH)
                self.photo_icon_main = ImageTk.PhotoImage(img_icon) 
                self.root.iconphoto(False, self.photo_icon_main)
        except Exception as e:
            print(f"Lỗi hiển thị icon: {e}")
            
        self.images = [] 
        self.preview_photo = None 
        self.full_layout_image = None 
        self.image_locations = [] 
        
        self.zoom_scale = 1.0 
        self.hover_rect_id = None 
        self.hover_image_index = -1 

        # --- GIAO DIỆN ---
        # 1. Khung điều khiển (Bên trái)
        control_frame = tk.Frame(root, bg="#2c3e50", width=300)
        control_frame.pack(side="left", fill="y")
        control_frame.pack_propagate(False) 

        self.lbl_title = tk.Label(control_frame, text="MENU", bg="#2c3e50", fg="white", font=("Helvetica", 16, "bold"))
        self.lbl_title.pack(pady=(20, 10))

        # --- CÁC NÚT CHỨC NĂNG ---
        
        # 1. Nút HDSD
        self.btn_guide = tk.Button(control_frame, text="HDSD", command=self.show_guide_window, 
                                   bg="#34495e", fg="white", font=("Arial", 10), padx=10, pady=5, width=20,
                                   activebackground="#546E7A", activeforeground="white", cursor="hand2")
        self.btn_guide.pack(pady=5)
        # Thêm hiệu ứng hover (Màu gốc: #34495e -> Hover: #546E7A)
        self.apply_hover_effect(self.btn_guide, "#34495e", "#546E7A")

        tk.Frame(control_frame, height=2, bg="white").pack(fill="x", padx=20, pady=10)

        # 2. Nút Chọn File (Tím)
        self.btn_load = tk.Button(control_frame, text="Chọn File Ảnh", command=self.load_from_files, 
                                   bg="#8e44ad", fg="white", font=("Arial", 11, "bold"), padx=10, pady=8, width=20,
                                   activebackground="#9b59b6", activeforeground="white", cursor="hand2")
        self.btn_load.pack(pady=(10, 5))
        # Hover (Tím đậm -> Tím nhạt)
        self.apply_hover_effect(self.btn_load, "#8e44ad", "#9b59b6")

        # 3. Nút Dán Ảnh (Xanh lá)
        self.btn_paste = tk.Button(control_frame, text="Dán Ảnh ", command=self.paste_from_clipboard, 
                                   bg="#27ae60", fg="white", font=("Arial", 11, "bold"), padx=10, pady=8, width=20,
                                   activebackground="#2ecc71", activeforeground="white", cursor="hand2")
        self.btn_paste.pack(pady=5)
        # Hover (Xanh đậm -> Xanh nhạt)
        self.apply_hover_effect(self.btn_paste, "#27ae60", "#2ecc71")

        # 4. Nút Reset (Đỏ)
        self.btn_reset = tk.Button(control_frame, text="Xóa & Làm Mới", command=self.reset_data, 
                                   bg="#c0392b", fg="white", font=("Arial", 11, "bold"), padx=10, pady=8, width=20,
                                   activebackground="#e74c3c", activeforeground="white", cursor="hand2")
        self.btn_reset.pack(pady=10)
        # Hover (Đỏ đậm -> Đỏ nhạt)
        self.apply_hover_effect(self.btn_reset, "#c0392b", "#e74c3c")

        self.lbl_count = tk.Label(control_frame, text="Số lượng: 0 ảnh", bg="#2c3e50", fg="#ecf0f1", font=("Arial", 12))
        self.lbl_count.pack(pady=10)
        
        tk.Label(control_frame, text="* Lăn chuột để Zoom\n* Click vào ảnh để Xóa", bg="#2c3e50", fg="#f1c40f", font=("Arial", 10, "italic")).pack(pady=5)

        # --- CREDIT ---
        tk.Frame(control_frame, height=2, bg="white").pack(fill="x", padx=20, pady=10)
        tk.Label(control_frame, text="Giao lưu và ủng hộ:", bg="#2c3e50", fg="#f50c0c", font=("Arial", 16, "italic")).pack(pady=(5, 10))

        # Hàm tạo link có hiệu ứng hover chữ
        def create_link_row(parent, text, link, icon_path=None):
            frame = tk.Frame(parent, bg="#2c3e50")
            frame.pack(pady=5, fill="x", padx=30)
            
            label_text = tk.Label(frame, text=text, bg="#2c3e50", fg="white", font=("Courier New", 14, "bold"), cursor="hand2")
            
            # Hiệu ứng hover cho Text: Đổi sang màu xanh dương sáng (#3498db)
            label_text.bind("<Enter>", lambda e: label_text.config(fg="#3498db"))
            label_text.bind("<Leave>", lambda e: label_text.config(fg="white"))
            
            try:
                img = Image.open(icon_path).resize((24, 24), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                lbl_icon = tk.Label(frame, image=photo, bg="#2c3e50", cursor="hand2")
                lbl_icon.image = photo
                lbl_icon.pack(side="left", padx=5)
                lbl_icon.bind("<Button-1>", lambda e: webbrowser.open(link))
            except Exception: pass
            
            label_text.pack(side="left", padx=5)
            label_text.bind("<Button-1>", lambda e: webbrowser.open(link))
            return label_text

        self.lbl_credit = create_link_row(control_frame, "By Darrk", LINK_FACEBOOK, ICON_FB_PATH)
        self.lbl_vps = create_link_row(control_frame, "VPS_Zang", LINK_VPS, ICON_VPS_PATH)
        self.lbl_zalo = create_link_row(control_frame, "Play_NRO_VPS", LINK_ZALO, ICON_ZALO_PATH)

        # 5. Nút Lưu (Xanh dương)
        self.btn_save = tk.Button(control_frame, text="LƯU FILE ẢNH", command=self.save_image, 
                                     bg="#2980b9", fg="white", font=("Arial", 12, "bold"), padx=10, pady=15, width=20,
                                     activebackground="#3498db", activeforeground="white", cursor="hand2")
        self.btn_save.pack(side="bottom", pady=40)
        # Hover (Xanh đậm -> Xanh nhạt)
        self.apply_hover_effect(self.btn_save, "#2980b9", "#3498db")

        # 2. Khung Preview (Bên phải)
        preview_container = tk.Frame(root, bg="#34495e")
        preview_container.pack(side="right", fill="both", expand=True)

        self.lbl_preview = tk.Label(preview_container, text="XEM TRƯỚC (PREVIEW)", bg="#34495e", fg="#bdc3c7", font=("Arial", 11, "bold"))
        self.lbl_preview.pack(pady=10)

        canvas_frame = tk.Frame(preview_container, bg="#222222")
        canvas_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.v_scroll = Scrollbar(canvas_frame, orient="vertical")
        self.h_scroll = Scrollbar(canvas_frame, orient="horizontal")

        self.canvas = tk.Canvas(canvas_frame, bg="#222222", bd=0, highlightthickness=0,
                                yscrollcommand=self.v_scroll.set, xscrollcommand=self.h_scroll.set)
        
        self.v_scroll.config(command=self.canvas.yview)
        self.h_scroll.config(command=self.canvas.xview)

        self.v_scroll.pack(side="right", fill="y")
        self.h_scroll.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.lbl_guide = tk.Label(self.canvas, text="Chưa có ảnh.\nHãy chọn ảnh hoặc dán ảnh.", 
                                  bg="#222222", fg="#777777", font=("Arial", 14))
        self.lbl_guide.place(relx=0.5, rely=0.5, anchor="center")

        # BINDINGS
        self.root.bind('<Control-v>', lambda e: self.paste_from_clipboard())
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)  
        self.canvas.bind("<Button-4>", self.on_mouse_wheel)    
        self.canvas.bind("<Button-5>", self.on_mouse_wheel)    
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<Button-1>", self.on_mouse_click)

        self.rainbow_colors = ["#FF0000", "#FF7F00", "#FFFF00", "#00FF00", "#0000FF", "#4B0082", "#9400D3"] 
        self.color_index = 0
        self.animate_rainbow_text()

    # --- [HÀM MỚI] XỬ LÝ HIỆU ỨNG HOVER ---
    def apply_hover_effect(self, widget, original_color, hover_color):
        """ Gán sự kiện đổi màu khi di chuột """
        widget.bind("<Enter>", lambda e: widget.config(bg=hover_color))
        widget.bind("<Leave>", lambda e: widget.config(bg=original_color))
    # -------------------------------------

    def show_guide_window(self):
        guide_win = Toplevel(self.root)
        guide_win.title("Ghi chú")
        guide_win.geometry("700x430")
        guide_win.config(bg="#ecf0f1")
        
        try:
            if os.path.exists(ICON_APP_PATH):
                guide_win.iconbitmap(ICON_APP_PATH)
                if hasattr(self, 'photo_icon_main'): 
                     guide_win.iconphoto(False, self.photo_icon_main)
        except Exception: pass

        tk.Label(guide_win, text="Ghi chú", font=("Arial", 14, "bold"), bg="#ecf0f1", fg="#2c3e50").pack(pady=10)
        
        guide_text = (
            "1. Thao tác cơ bản:\n"
            "   - Thêm ảnh: Chọn file hoặc Dán (Ctrl+V).\n"
            "   - Lưu ảnh: Bấm 'LƯU FILE ẢNH'.\n\n"
            "2. Tương tác Preview:\n"
            "   - Phóng to/Thu nhỏ: Lăn con lăn chuột tại vùng xem trước.\n"
            "   - Xóa ảnh lẻ: Di chuột vào ảnh muốn xóa (hiện khung đỏ) rồi bấm chuột trái.\n\n"
            "3. Lưu ý:\n"
            "   - Ảnh được tự động sắp xếp từ trái qua phải, xuống dòng.\n"
                "Cảm ơn mọi người đã tin tưởng và sử dụng, mọi góp ý về app/tool\n "
                "Vui lòng nhắn qua fb giúp mình ợ :>"
        )
        tk.Label(guide_win, text=guide_text, font=("Arial", 13), justify="left", bg="#ecf0f1", padx=20).pack(fill="both")
        
        btn_ok = tk.Button(guide_win, text="Đã Hiểu", command=guide_win.destroy, 
                           bg="#27ae60", fg="white", width=20, cursor="hand2")
        btn_ok.pack(pady=30)
        self.apply_hover_effect(btn_ok, "#27ae60", "#2ecc71")

    def load_from_files(self):
        file_paths = filedialog.askopenfilenames(
            title="Chọn ảnh",
            filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.bmp;*.webp;*.tiff")]
        )
        if file_paths:
            count_new = 0
            for path in file_paths:
                try:
                    img = Image.open(path)
                    self.add_image(img)
                    count_new += 1
                except Exception as e:
                    print(f"Lỗi file {path}: {e}")
            if count_new > 0:
                self.update_ui_after_change()

    def animate_rainbow_text(self):
        current_color = self.rainbow_colors[self.color_index]
        self.lbl_title.config(fg=current_color)   
        self.lbl_preview.config(fg=current_color) 
        self.lbl_credit.config(fg=current_color) 
        self.lbl_vps.config(fg=current_color)    
        self.lbl_zalo.config(fg=current_color)    
        self.color_index = (self.color_index + 1) % len(self.rainbow_colors)
        self.root.after(200, self.animate_rainbow_text)

    def reset_data(self):
        if not self.images: return
        if messagebox.askyesno("Xác nhận", "Xóa toàn bộ ảnh và làm mới?"):
            self.images = []
            self.full_layout_image = None
            self.image_locations = []
            self.lbl_count.config(text="Số lượng: 0 ảnh")
            self.canvas.delete("all")
            self.lbl_guide.place(relx=0.5, rely=0.5, anchor="center")
            self.zoom_scale = 1.0

    def paste_from_clipboard(self):
        try:
            clipboard_data = ImageGrab.grabclipboard()
            new_count = 0
            if clipboard_data is None:
                try:
                    text = self.root.clipboard_get()
                    if os.path.isfile(text): 
                        self.add_image(Image.open(text))
                        new_count = 1
                except: pass
            elif isinstance(clipboard_data, Image.Image):
                self.add_image(clipboard_data)
                new_count = 1
            elif isinstance(clipboard_data, list):
                for path in clipboard_data:
                    if isinstance(path, str) and os.path.isfile(path):
                        try: 
                            self.add_image(Image.open(path))
                            new_count += 1
                        except: pass
            if new_count > 0:
                self.update_ui_after_change()
        except Exception as e:
            print(f"Error Paste: {e}")

    def add_image(self, img):
        if img.mode != 'RGB': img = img.convert('RGB')
        self.images.append(img)
    
    def update_ui_after_change(self):
        self.lbl_count.config(text=f"Số lượng: {len(self.images)} ảnh")
        self.generate_full_layout() 
        self.draw_preview() 

    def generate_full_layout(self):
        if not self.images: 
            self.full_layout_image = None
            self.image_locations = []
            return

        pool = []
        for idx, img in enumerate(self.images):
            pool.append({'img': img, 'aspect': img.width / img.height, 'original_index': idx})

        target_row_aspect = TARGET_CANVAS_WIDTH / ROW_BASE_HEIGHT
        final_rows = []
        temp_pool = list(pool) 

        while temp_pool:
            current_row = []
            current_row_aspect = 0.0
            while temp_pool:
                best_idx = -1
                min_diff = float('inf')
                if not current_row:
                    best_idx = 0 
                else:
                    remainder = target_row_aspect - current_row_aspect
                    for i, item in enumerate(temp_pool):
                        diff = abs(item['aspect'] - remainder)
                        if diff < min_diff:
                            min_diff = diff
                            best_idx = i
                
                if best_idx != -1:
                    candidate = temp_pool[best_idx]
                    if current_row_aspect > target_row_aspect * 0.85:
                            if (current_row_aspect + candidate['aspect']) > target_row_aspect * 1.25:
                                break 
                    current_row.append(candidate)
                    current_row_aspect += candidate['aspect']
                    temp_pool.pop(best_idx)
                    if current_row_aspect >= target_row_aspect: break
                else:
                    break
            if current_row:
                final_rows.append({'items': current_row, 'aspect_sum': current_row_aspect})

        total_height = 0
        render_rows = []
        for row_data in final_rows:
            items = row_data['items']
            aspect_sum = row_data['aspect_sum']
            row_height = int(TARGET_CANVAS_WIDTH / aspect_sum)
            if row_data == final_rows[-1] and aspect_sum < target_row_aspect * 0.7:
                    row_height = ROW_BASE_HEIGHT
            render_rows.append({'items': items, 'height': row_height})
            total_height += row_height

        self.full_layout_image = Image.new('RGB', (TARGET_CANVAS_WIDTH, total_height), (255, 255, 255))
        self.image_locations = [] 

        y_offset = 0
        for row in render_rows:
            h = row['height']
            x_offset = 0
            items = row['items']
            for idx, item in enumerate(items):
                if idx == len(items) - 1 and h != ROW_BASE_HEIGHT:
                    w = TARGET_CANVAS_WIDTH - x_offset
                else:
                    w = int(h * item['aspect'])
                
                img_resized = item['img'].resize((w, h), Image.LANCZOS)
                self.full_layout_image.paste(img_resized, (x_offset, y_offset))
                self.image_locations.append((x_offset, y_offset, w, h, item['original_index']))
                x_offset += w
            y_offset += h

    def draw_preview(self):
        if not self.full_layout_image: return
        self.lbl_guide.place_forget()
        base_scale = 0.2 
        current_w = int(self.full_layout_image.width * base_scale * self.zoom_scale)
        current_h = int(self.full_layout_image.height * base_scale * self.zoom_scale)
        
        if current_w < 1 or current_h < 1: return

        preview_img = self.full_layout_image.resize((current_w, current_h), Image.NEAREST)
        self.preview_photo = ImageTk.PhotoImage(preview_img)
        
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.preview_photo)
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def on_mouse_wheel(self, event):
        if not self.full_layout_image: return
        if event.num == 5 or event.delta < 0:
            self.zoom_scale /= 1.1 
        if event.num == 4 or event.delta > 0:
            self.zoom_scale *= 1.1 
        if self.zoom_scale < 0.2: self.zoom_scale = 0.2
        if self.zoom_scale > 5.0: self.zoom_scale = 5.0
        self.draw_preview()

    def on_mouse_move(self, event):
        if not self.full_layout_image: return
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)
        base_scale = 0.2 
        current_display_scale = base_scale * self.zoom_scale
        real_x = cx / current_display_scale
        real_y = cy / current_display_scale

        found = False
        for loc in self.image_locations:
            x, y, w, h, original_idx = loc
            if x <= real_x <= x + w and y <= real_y <= y + h:
                if self.hover_image_index != original_idx:
                    self.hover_image_index = original_idx
                    self.canvas.delete("highlight")
                    disp_x = x * current_display_scale
                    disp_y = y * current_display_scale
                    disp_w = w * current_display_scale
                    disp_h = h * current_display_scale
                    self.canvas.create_rectangle(disp_x, disp_y, disp_x+disp_w, disp_y+disp_h, 
                                                 outline="red", width=3, tags="highlight")
                    self.canvas.create_rectangle(disp_x, disp_y, disp_x+disp_w, disp_y+disp_h, 
                                                 fill="red", stipple="gray25", tags="highlight") 
                    self.canvas.config(cursor="hand2")
                found = True
                break
        
        if not found and self.hover_image_index != -1:
            self.hover_image_index = -1
            self.canvas.delete("highlight")
            self.canvas.config(cursor="")

    def on_mouse_click(self, event):
        if self.hover_image_index != -1:
            if 0 <= self.hover_image_index < len(self.images):
                del self.images[self.hover_image_index]
                self.hover_image_index = -1
                self.canvas.delete("highlight")
                self.canvas.config(cursor="")
                self.update_ui_after_change()

    def save_image(self):
        if not self.images:
            messagebox.showwarning("Cảnh báo", "Chưa có ảnh nào!")
            return
        save_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPG", "*.jpg")])
        if not save_path: return
        try:
            self.root.config(cursor="watch")
            self.root.update()
            self.generate_full_layout()
            if self.full_layout_image:
                self.full_layout_image.save(save_path, quality=95)
                messagebox.showinfo("Thành công", f"Đã lưu ảnh tại:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))
        finally:
            self.root.config(cursor="")

if __name__ == "__main__":
    try:
        myappid = 'darrk.imagejoiner.version.2' 
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except: pass

    root = tk.Tk()
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except: pass
        
    app = AutoArrangePreviewApp(root)
    root.mainloop()