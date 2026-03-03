import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import webbrowser
import subprocess
import json
import os
from PIL import Image, ImageTk  # 已移到顶部，警告消失

CONFIG_FILE = "config.json"
SETTING_FILE = "settings.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_config(data):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_settings():
    if os.path.exists(SETTING_FILE):
        with open(SETTING_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "theme": "light",
        "bg_image": ""
    }

def save_settings(settings):
    with open(SETTING_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)

class AppLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("⚙️ huasheng快捷启动器")
        self.root.geometry("500x680")
        self.root.resizable(False, False)

        self.items = load_config()
        self.settings = load_settings()
        self.bg_photo = None

        self.setup_theme()
        self.create_widgets()
        self.apply_theme()
        self.refresh_list()

    def setup_theme(self):
        self.colors = {
            "light": {
                "bg": "#ffffff",
                "fg": "#222222",
                "card": "#f8f9fa",
                "frame": "#eeeeee"
            },
            "dark": {
                "bg": "#2b2b2b",
                "fg": "#ffffff",
                "card": "#3a3a3a",
                "frame": "#444444"
            }
        }

    def create_widgets(self):
        top_frame = ttk.Frame(self.root, padding=10)
        top_frame.pack(fill=tk.X)
        ttk.Label(top_frame, text="⚙️ huasheng的快捷启动器", font=("微软雅黑", 16, "bold")).pack(side=tk.LEFT)
        ttk.Button(top_frame, text="⚙ 设置", command=self.open_settings).pack(side=tk.RIGHT)

        add_frame = ttk.LabelFrame(self.root, text="➕ 添加快捷方式", padding=15)
        add_frame.pack(fill=tk.X, padx=15, pady=5)

        ttk.Label(add_frame, text="名称：").grid(row=0, column=0, sticky="w", padx=5, pady=6)
        self.entry_name = ttk.Entry(add_frame, width=20)
        self.entry_name.grid(row=0, column=1, padx=5, pady=6)

        ttk.Label(add_frame, text="路径/网址：").grid(row=1, column=0, sticky="w", padx=5, pady=6)
        self.entry_path = ttk.Entry(add_frame, width=38)
        self.entry_path.grid(row=1, column=1, padx=5, pady=6)

        self.type_var = tk.StringVar(value="url")
        ttk.Radiobutton(add_frame, text="🌐 网页", variable=self.type_var, value="url").grid(row=2, column=0)
        ttk.Radiobutton(add_frame, text="🖥️ 应用", variable=self.type_var, value="app").grid(row=2, column=1)

        ttk.Button(add_frame, text="添加", command=self.add_item).grid(row=3, column=0, columnspan=2, pady=8)

        list_frame = ttk.LabelFrame(self.root, text="📋 快捷列表", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        self.canvas = tk.Canvas(list_frame)
        self.scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.content_frame = ttk.Frame(self.canvas)

        self.content_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.add_frame = add_frame
        self.list_frame = list_frame
        self.top_frame = top_frame

    def apply_theme(self):
        theme = self.settings["theme"]
        c = self.colors[theme]
        self.root.configure(bg=c["bg"])
        self.canvas.config(bg=c["bg"])

        style = ttk.Style()
        style.configure(f"{theme}.TLabelframe", background=c["frame"], foreground=c["fg"])
        style.configure(f"{theme}.TLabelframe.Label", background=c["frame"], foreground=c["fg"])
        style.configure("Card.TFrame", background=c["card"])
        style.configure("TButton", font=("微软雅黑", 10))

        bg_img = self.settings.get("bg_image", "")
        if bg_img and os.path.exists(bg_img):
            try:
                img = Image.open(bg_img)
                img = img.resize((500, 680), Image.Resampling.LANCZOS)
                self.bg_photo = ImageTk.PhotoImage(img)
                self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")
            except:
                pass

    def open_settings(self):
        win = tk.Toplevel(self.root)
        win.title("设置")
        win.geometry("360x220")
        win.resizable(False, False)

        ttk.Label(win, text="🌗 主题模式", font=("bold", 12)).pack(anchor="w", padx=15, pady=8)
        theme_var = tk.StringVar(value=self.settings["theme"])
        ttk.Radiobutton(win, text="白天模式", variable=theme_var, value="light").pack(anchor="w", padx=25)
        ttk.Radiobutton(win, text="黑夜模式", variable=theme_var, value="dark").pack(anchor="w", padx=25)

        ttk.Label(win, text="🖼️ 自定义背景图片", font=("bold", 12)).pack(anchor="w", padx=15, pady=8)
        path_var = tk.StringVar(value=self.settings.get("bg_image", ""))
        entry = ttk.Entry(win, textvariable=path_var, width=30)
        entry.pack(side=tk.LEFT, padx=15, pady=5)

        def choose_bg():
            f = filedialog.askopenfilename(filetypes=[("图片", "*.png *.jpg *.jpeg")])
            if f:
                path_var.set(f)

        ttk.Button(win, text="选择", command=choose_bg).pack(side=tk.LEFT, padx=5, pady=5)

        def save():
            self.settings["theme"] = theme_var.get()
            self.settings["bg_image"] = path_var.get()
            save_settings(self.settings)
            self.apply_theme()
            messagebox.showinfo("成功", "设置已保存！")
            win.destroy()

        ttk.Button(win, text="✅ 保存设置", command=save).pack(pady=10)

    def add_item(self):
        name = self.entry_name.get().strip()
        path = self.entry_path.get().strip()
        typ = self.type_var.get()
        if not name or not path:
            messagebox.showwarning("提示", "名称和路径不能为空")
            return
        self.items.append({"name": name, "type": typ, "path": path})
        save_config(self.items)
        self.entry_name.delete(0, tk.END)
        self.entry_path.delete(0, tk.END)
        self.refresh_list()

    def launch(self, path, typ, admin=False):
        if typ == "url":
            webbrowser.open(path)
            return
        try:
            if admin:
                subprocess.Popen(
                    ["powershell", "-Command", f"Start-Process '{path}' -Verb RunAs"],
                    shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
            else:
                subprocess.Popen(path, shell=True)
        except:
            messagebox.showerror("错误", "无法打开程序")

    def delete_item(self, idx):
        del self.items[idx]
        save_config(self.items)
        self.refresh_list()

    def refresh_list(self):
        for w in self.content_frame.winfo_children():
            w.destroy()

        for idx, item in enumerate(self.items):
            card = ttk.Frame(self.content_frame, style="Card.TFrame")
            card.pack(fill=tk.X, pady=5, padx=8)

            ttk.Button(
                card, text=item["name"], width=18,
                command=lambda it=item: self.launch(it["path"], it["type"], False)
            ).pack(side=tk.LEFT, padx=5, pady=6)

            if item["type"] == "app":
                ttk.Button(
                    card, text="管理员", width=8,
                    command=lambda it=item: self.launch(it["path"], it["type"], True)
                ).pack(side=tk.LEFT, padx=5)

            ttk.Button(
                card, text="删除", width=6,
                command=lambda i=idx: self.delete_item(i)
            ).pack(side=tk.RIGHT, padx=5)

if __name__ == "__main__":
    root = tk.Tk()
    AppLauncher(root)
    root.mainloop()