import os
import re
import sys
import shutil
import threading
import subprocess
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox

APP_NAME = "LJ Convert"
CREATE_NO_WINDOW = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


def find_tool(name):
    local_path = resource_path(os.path.join("bin", name))
    if os.path.exists(local_path):
        return local_path

    found = shutil.which(name)
    if found:
        return found

    return None


def find_program(base_name):
    if os.name == "nt":
        return find_tool(base_name + ".exe") or find_tool(base_name)
    return find_tool(base_name)


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#%02x%02x%02x" % rgb


def blend(c1, c2, t):
    a = hex_to_rgb(c1)
    b = hex_to_rgb(c2)
    return rgb_to_hex(tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3)))


def vertical_gradient(canvas, x1, y1, x2, y2, top, bottom, steps=None):
    if steps is None:
        steps = max(1, y2 - y1)

    for i in range(steps):
        t = i / max(1, steps - 1)
        color = blend(top, bottom, t)
        yy1 = y1 + int((y2 - y1) * i / steps)
        yy2 = y1 + int((y2 - y1) * (i + 1) / steps)
        canvas.create_rectangle(x1, yy1, x2, yy2, outline=color, fill=color)


def rounded_rect(canvas, x1, y1, x2, y2, radius=18, **kwargs):
    points = [
        x1 + radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)


class AeroButton(tk.Canvas):
    def __init__(self, master, text, command=None, width=112, height=30, font=("Tahoma", 9, "bold")):
        super().__init__(
            master,
            width=width,
            height=height,
            bg="#dff7ff",
            bd=0,
            highlightthickness=0,
            cursor="hand2"
        )
        self.text = text
        self.command = command
        self.width = width
        self.height = height
        self.font = font
        self.enabled = True
        self.hover = False
        self.down = False

        self.bind("<Enter>", self._enter)
        self.bind("<Leave>", self._leave)
        self.bind("<ButtonPress-1>", self._press)
        self.bind("<ButtonRelease-1>", self._release)
        self.draw()

    def set_enabled(self, enabled):
        self.enabled = enabled
        self.configure(cursor="hand2" if enabled else "arrow")
        self.draw()

    def _enter(self, _event):
        if self.enabled:
            self.hover = True
            self.draw()

    def _leave(self, _event):
        self.hover = False
        self.down = False
        self.draw()

    def _press(self, _event):
        if self.enabled:
            self.down = True
            self.draw()

    def _release(self, _event):
        if self.enabled and self.down and self.command:
            self.down = False
            self.draw()
            self.command()
        else:
            self.down = False
            self.draw()

    def draw(self):
        self.delete("all")

        if not self.enabled:
            top, bottom, border, text_color = "#cfd8dd", "#9ea9af", "#7f8a91", "#5f6b72"
        elif self.down:
            top, bottom, border, text_color = "#33a5e9", "#0d6fc2", "#07599c", "#ffffff"
        elif self.hover:
            top, bottom, border, text_color = "#b9fbff", "#1b93ea", "#0075c8", "#053e6b"
        else:
            top, bottom, border, text_color = "#ffffff", "#38b5f6", "#1684cf", "#054b79"

        if self.enabled and self.hover:
            rounded_rect(self, 1, 1, self.width - 1, self.height - 1, 11, fill="#94f6ff", outline="")

        rounded_rect(self, 3, 3, self.width - 3, self.height - 3, 10, fill=bottom, outline=border, width=1)
        vertical_gradient(self, 4, 4, self.width - 4, self.height - 4, top, bottom, steps=24)

        rounded_rect(self, 7, 6, self.width - 7, int(self.height * 0.52), 8, fill="#ffffff", outline="")
        self.create_rectangle(8, int(self.height * 0.31), self.width - 8, int(self.height * 0.54), fill=blend("#ffffff", top, 0.25), outline="")
        self.create_line(10, self.height - 7, self.width - 10, self.height - 7, fill="#05619f")

        y_offset = 1 if self.down else 0
        self.create_text(
            self.width / 2,
            self.height / 2 + y_offset,
            text=self.text,
            fill=text_color,
            font=self.font
        )


class AeroProgressBar(tk.Canvas):
    def __init__(self, master, width=405, height=28, segments=28):
        super().__init__(master, width=width, height=height, bg="#dff7ff", bd=0, highlightthickness=0)
        self.width = width
        self.height = height
        self.segments = segments
        self.progress = 0
        self.draw_bar()

    def set_progress(self, value):
        self.progress = max(0, min(100, value))
        self.draw_bar()

    def draw_bar(self):
        self.delete("all")

        rounded_rect(self, 0, 0, self.width, self.height, 12, fill="#2f85bd", outline="#ffffff", width=1)
        rounded_rect(self, 2, 2, self.width - 2, self.height - 2, 10, fill="#c8efff", outline="#1a78b4", width=1)
        vertical_gradient(self, 3, 3, self.width - 3, self.height - 3, "#f9ffff", "#9fd6ed", steps=24)

        padding = 5
        gap = 3
        usable_width = self.width - padding * 2
        segment_width = (usable_width - gap * (self.segments - 1)) / self.segments
        filled_segments = int((self.progress / 100) * self.segments)

        for i in range(self.segments):
            x1 = padding + i * (segment_width + gap)
            y1 = padding
            x2 = x1 + segment_width
            y2 = self.height - padding

            if i < filled_segments:
                self.create_rectangle(x1, y1, x2, y2, fill="#009dff", outline="#0067b8")
                self.create_rectangle(x1 + 1, y1 + 1, x2 - 1, y1 + 6, fill="#bfffff", outline="")
                self.create_rectangle(x1 + 1, y1 + 7, x2 - 1, y2 - 1, fill="#0877df", outline="")
                self.create_line(x1 + 2, y2 - 2, x2 - 2, y2 - 2, fill="#39e7ff")
            else:
                self.create_rectangle(x1, y1, x2, y2, fill="#e9fbff", outline="#94cce0")
                self.create_rectangle(x1 + 1, y1 + 1, x2 - 1, y1 + 5, fill="#ffffff", outline="")

        self.create_line(11, 5, self.width - 11, 5, fill="#ffffff")


class LJConvertApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry("620x430")
        self.root.resizable(False, False)
        self.root.configure(bg="#7bdfff")

        self.input_file = tk.StringVar()
        self.youtube_url = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.convert_type = tk.StringVar(value="mp4")
        self.status_text = tk.StringVar(value="Ready.")

        self.ffmpeg_path = find_program("ffmpeg")
        self.ffprobe_path = find_program("ffprobe")
        self.ytdlp_path = find_program("yt-dlp")

        self.bg = tk.Canvas(root, width=620, height=430, highlightthickness=0, bd=0)
        self.bg.place(x=0, y=0)

        self.build_ui()

    def build_ui(self):
        self.draw_background()

        entry_style = {
            "font": ("Tahoma", 9),
            "relief": "flat",
            "bd": 0,
            "bg": "#ffffff",
            "fg": "#064663",
            "insertbackground": "#0a75bd",
            "highlightthickness": 2,
            "highlightbackground": "#82cfea",
            "highlightcolor": "#00a8ff",
        }

        self.bg.create_text(42, 103, text="Online video URL", anchor="w", fill="#07547a", font=("Tahoma", 9, "bold"))
        self.bg.create_text(173, 103, text="only use files you have permission to download", anchor="w", fill="#4c8ba6", font=("Tahoma", 8))
        self.url_entry = tk.Entry(self.root, textvariable=self.youtube_url, width=55, **entry_style)
        self.url_entry.place(x=42, y=119, height=25)

        self.bg.create_text(42, 160, text="Local video file", anchor="w", fill="#07547a", font=("Tahoma", 9, "bold"))
        self.input_entry = tk.Entry(self.root, textvariable=self.input_file, width=43, **entry_style)
        self.input_entry.place(x=42, y=176, height=25)

        self.browse_button = AeroButton(self.root, "Browse...", command=self.browse_input, width=102, height=30)
        self.browse_button.place(x=468, y=173)

        self.bg.create_text(42, 224, text="Convert to", anchor="w", fill="#07547a", font=("Tahoma", 9, "bold"))

        radio_style = {
            "font": ("Tahoma", 9, "bold"),
            "bg": "#dff7ff",
            "fg": "#064663",
            "activebackground": "#dff7ff",
            "activeforeground": "#006fb5",
            "selectcolor": "#ffffff",
            "bd": 0,
            "highlightthickness": 0,
            "cursor": "hand2",
        }
        self.mp4_radio = tk.Radiobutton(self.root, text="MP4 video", variable=self.convert_type, value="mp4", **radio_style)
        self.mp3_radio = tk.Radiobutton(self.root, text="MP3 audio", variable=self.convert_type, value="mp3", **radio_style)
        self.mp4_radio.place(x=126, y=213)
        self.mp3_radio.place(x=228, y=213)

        self.bg.create_text(42, 267, text="Output folder", anchor="w", fill="#07547a", font=("Tahoma", 9, "bold"))
        self.output_entry = tk.Entry(self.root, textvariable=self.output_folder, width=43, **entry_style)
        self.output_entry.place(x=42, y=283, height=25)

        self.output_button = AeroButton(self.root, "Browse...", command=self.browse_output, width=102, height=30)
        self.output_button.place(x=468, y=280)

        self.convert_button = AeroButton(self.root, "Convert", command=self.start_conversion, width=126, height=34, font=("Tahoma", 10, "bold"))
        self.convert_button.place(x=42, y=332)

        self.bg.create_text(190, 330, text="Progress", anchor="w", fill="#07547a", font=("Tahoma", 9, "bold"))
        self.progress_bar = AeroProgressBar(self.root, width=380, height=30, segments=26)
        self.progress_bar.place(x=190, y=346)

        self.status_item = self.bg.create_text(
            42,
            398,
            text=self.status_text.get(),
            anchor="w",
            fill="#ffffff",
            font=("Tahoma", 9, "bold")
        )

    def draw_background(self):
        c = self.bg
        vertical_gradient(c, 0, 0, 620, 430, "#39bfff", "#e8ffff", steps=430)

        c.create_oval(-90, 260, 740, 560, fill="#74d35d", outline="")
        c.create_oval(-80, 285, 700, 550, fill="#a7ec67", outline="")
        c.create_oval(170, 300, 720, 515, fill="#37b8db", outline="")

        for x, y, size, color in [
            (478, 32, 106, "#cfffff"),
            (520, 88, 55, "#ffffff"),
            (61, 62, 72, "#ffffff"),
            (557, 236, 46, "#d7ffff"),
            (91, 340, 34, "#dfffff"),
            (397, 256, 28, "#ffffff"),
        ]:
            c.create_oval(x, y, x + size, y + size, fill=color, outline="#ffffff")
            c.create_oval(x + 8, y + 7, x + int(size * 0.58), y + int(size * 0.36), fill="#ffffff", outline="")

        c.create_arc(-130, 20, 500, 470, start=8, extent=33, style="arc", outline="#ffffff", width=4)
        c.create_arc(-60, 84, 535, 465, start=10, extent=30, style="arc", outline="#94f7ff", width=2)
        c.create_arc(150, -90, 740, 360, start=196, extent=34, style="arc", outline="#ffffff", width=3)

        c.create_text(34, 35, text="LJ Convert", anchor="w", fill="#006194", font=("Trebuchet MS", 26, "bold"))
        c.create_text(32, 32, text="LJ Convert", anchor="w", fill="#ffffff", font=("Trebuchet MS", 26, "bold"))
        c.create_text(36, 64, text="made by ljgames", anchor="w", fill="#eaffff", font=("Tahoma", 9, "bold"))

        rounded_rect(c, 25, 82, 595, 388, 24, fill="#0a6a97", outline="")
        rounded_rect(c, 21, 78, 591, 384, 24, fill="#dff7ff", outline="#ffffff", width=2)
        vertical_gradient(c, 24, 81, 588, 381, "#ffffff", "#b6ecff", steps=80)
        rounded_rect(c, 30, 87, 582, 182, 21, fill="#ffffff", outline="")
        c.create_rectangle(31, 128, 581, 186, fill="#dff7ff", outline="")
        c.create_line(42, 206, 570, 206, fill="#9ed9ee")
        c.create_line(42, 252, 570, 252, fill="#9ed9ee")
        c.create_line(42, 320, 570, 320, fill="#9ed9ee")

        rounded_rect(c, 433, 36, 585, 65, 14, fill="#05a9f4", outline="#ffffff", width=1)
        c.create_rectangle(438, 39, 580, 49, fill="#baffff", outline="")
        c.create_text(509, 51, text="LJGAMES", fill="#ffffff", font=("Tahoma", 8, "bold"))

        rounded_rect(c, 21, 390, 591, 418, 13, fill="#109bd8", outline="#ffffff", width=1)
        c.create_rectangle(30, 393, 582, 401, fill="#8fffff", outline="")

    def set_status(self, text):
        self.status_text.set(text)
        self.bg.itemconfigure(self.status_item, text=text)

    def browse_input(self):
        file_path = filedialog.askopenfilename(
            title="Choose a video file",
            filetypes=[
                ("Video files", "*.mp4 *.mov *.mkv *.avi *.webm *.flv *.wmv *.m4v"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.input_file.set(file_path)
            self.youtube_url.set("")
            if not self.output_folder.get():
                self.output_folder.set(os.path.dirname(file_path))

    def browse_output(self):
        folder = filedialog.askdirectory(title="Choose output folder")
        if folder:
            self.output_folder.set(folder)

    def start_conversion(self):
        if not self.ffmpeg_path or not self.ffprobe_path:
            messagebox.showerror(APP_NAME, "FFmpeg or FFprobe was not found. Put them in the bin folder or add FFmpeg to PATH.")
            return

        youtube_url = self.youtube_url.get().strip()
        input_path = self.input_file.get().strip()
        output_dir = self.output_folder.get().strip()
        output_type = self.convert_type.get()

        if not youtube_url and not input_path:
            messagebox.showwarning(APP_NAME, "Enter an online video URL or select a local file.")
            return

        if not output_dir or not os.path.exists(output_dir):
            messagebox.showerror(APP_NAME, "Choose a valid output folder.")
            return

        self.convert_button.set_enabled(False)
        self.progress_bar.set_progress(0)
        self.set_status("Starting...")

        thread = threading.Thread(
            target=self.process_input,
            args=(youtube_url, input_path, output_dir, output_type),
            daemon=True
        )
        thread.start()

    def process_input(self, youtube_url, input_path, output_dir, output_type):
        try:
            if youtube_url:
                self.root.after(0, lambda: self.set_status("Downloading permitted video..."))
                input_path = self.download_youtube(youtube_url)
                if not input_path:
                    self.root.after(0, self.finish_error)
                    return

            self.root.after(0, lambda: self.set_status("Converting..."))
            self.convert_video(input_path, output_dir, output_type)

        except Exception as e:
            self.root.after(0, lambda: self.finish_error(str(e)))

    def download_youtube(self, url):
        if not self.ytdlp_path:
            self.root.after(0, lambda: messagebox.showerror(
                APP_NAME,
                "yt-dlp was not found. Put yt-dlp.exe in the bin folder or add it to PATH."
            ))
            return None

        temp_dir = tempfile.mkdtemp(prefix="lj_convert_")
        output_template = os.path.join(temp_dir, "%(title).180B.%(ext)s")

        command = [
            self.ytdlp_path,
            "--newline",
            "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "--merge-output-format", "mp4",
            "-o", output_template,
            url
        ]

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            creationflags=CREATE_NO_WINDOW
        )

        for line in process.stdout:
            match = re.search(r"(\d+(?:\.\d+)?)%", line)
            if "[download]" in line and match:
                percent = int(float(match.group(1)))
                self.root.after(0, lambda p=percent: self.update_progress(p, "Downloading"))

        process.wait()

        if process.returncode != 0:
            return None

        for file in os.listdir(temp_dir):
            if file.lower().endswith((".mp4", ".webm", ".mkv", ".mov")):
                return os.path.join(temp_dir, file)

        return None

    def get_duration(self, input_path):
        command = [
            self.ffprobe_path,
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            input_path
        ]
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=CREATE_NO_WINDOW
        )
        try:
            return float(result.stdout.strip())
        except Exception:
            return 0

    def make_output_path(self, input_path, output_dir, output_type):
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        safe_name = re.sub(r'[<>:"/\\|?*]', "_", base_name)
        return os.path.join(output_dir, f"{safe_name}_converted.{output_type}")

    def convert_video(self, input_path, output_dir, output_type):
        duration = self.get_duration(input_path)
        output_path = self.make_output_path(input_path, output_dir, output_type)

        if output_type == "mp4":
            command = [
                self.ffmpeg_path,
                "-y",
                "-i", input_path,
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", "23",
                "-c:a", "aac",
                "-b:a", "192k",
                "-movflags", "+faststart",
                output_path
            ]
        else:
            command = [
                self.ffmpeg_path,
                "-y",
                "-i", input_path,
                "-vn",
                "-c:a", "libmp3lame",
                "-q:a", "2",
                output_path
            ]

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            creationflags=CREATE_NO_WINDOW
        )

        for line in process.stdout:
            if "time=" in line and duration > 0:
                try:
                    time_str = line.split("time=")[1].split()[0]
                    h, m, s = time_str.split(":")
                    current_seconds = int(h) * 3600 + int(m) * 60 + float(s)
                    percent = int((current_seconds / duration) * 100)
                    self.root.after(0, lambda p=percent: self.update_progress(p, "Converting"))
                except Exception:
                    pass

        process.wait()

        if process.returncode == 0:
            self.root.after(0, lambda: self.finish_success(output_path))
        else:
            self.root.after(0, self.finish_error)

    def update_progress(self, percent, label="Converting"):
        self.progress_bar.set_progress(percent)
        self.set_status(f"{label}... {percent}%")

    def finish_success(self, output_path):
        self.progress_bar.set_progress(100)
        self.set_status("Finished! Saved successfully.")
        self.convert_button.set_enabled(True)
        messagebox.showinfo(APP_NAME, f"Conversion finished!\n\nSaved as:\n{output_path}")

    def finish_error(self, error_message=None):
        self.set_status("Conversion failed.")
        self.convert_button.set_enabled(True)
        if error_message:
            messagebox.showerror(APP_NAME, f"Conversion failed:\n\n{error_message}")
        else:
            messagebox.showerror(APP_NAME, "Conversion failed.")


if __name__ == "__main__":
    root = tk.Tk()
    app = LJConvertApp(root)
    root.mainloop()
