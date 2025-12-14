#!/usr/bin/env python3
"""Simple macOS native file-picker uploader to run `main.py` on a chosen video file.

This avoids installing tkinter. It uses AppleScript (`osascript`) to present a file
picker and then spawns `main.py --video <path>` using the same Python interpreter.

Usage:
    python gui_uploader.py --host 127.0.0.1 --port 8000

Controls:
    After selecting a file the script will start processing. Press Ctrl+C to stop.
"""
import argparse
import os
import shlex
import signal
import subprocess
import sys


def choose_file_mac():
    # Use AppleScript to show a native file chooser and return POSIX path
    applescript = 'POSIX path of (choose file with prompt "Select a video file")'
    try:
        out = subprocess.check_output(["osascript", "-e", applescript], stderr=subprocess.DEVNULL)
        path = out.decode("utf-8").strip()
        return path
    except subprocess.CalledProcessError:
        return None


def run_main_with_file(python_exe, main_py, video_path, host, port):
    cmd = [python_exe, main_py, "--video", video_path, "--host", host, "--port", str(port)]
    print("Starting:", " ".join(shlex.quote(c) for c in cmd))
    proc = subprocess.Popen(cmd)
    return proc


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--host', default='127.0.0.1')
    p.add_argument('--port', type=int, default=8000)
    return p.parse_args()


def main():
    args = parse_args()
    root = os.path.dirname(__file__)
    main_py = os.path.join(root, 'main.py')

    if not os.path.exists(main_py):
        print('main.py not found in', root)
        return

    print('Please choose a video file in the dialog...')
    video = choose_file_mac()
    if not video:
        print('No file selected. Exiting.')
        return

    print('Selected:', video)
    proc = run_main_with_file(sys.executable, main_py, video, args.host, args.port)

    try:
        proc.wait()
    except KeyboardInterrupt:
        print('\nStopping processing...')
        try:
            proc.send_signal(signal.SIGINT)
            proc.wait(timeout=5)
        except Exception:
            proc.terminate()


if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""Simple Tkinter GUI to pick a video file and start/stop `main.py` processing.

Usage:
    python gui_uploader.py

Notes:
 - This spawns `main.py` in the same Python interpreter so your venv is used.
 - Defaults to `--host 127.0.0.1 --port 8000` but you can change them in the UI.
"""
import os
import signal
import subprocess
import sys
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox


ROOT = os.path.dirname(__file__)
MAIN_PY = os.path.join(ROOT, "main.py")


class GuiUploader:
    def __init__(self):
        self.proc = None
        self.filepath = None

        self.root = tk.Tk()
        self.root.title("Light2Max - File Uploader")

        frm = tk.Frame(self.root, padx=10, pady=10)
        frm.pack()

        tk.Button(frm, text="Select Video", command=self.select_file).grid(row=0, column=0)
        self.lbl_file = tk.Label(frm, text="(no file selected)", width=60, anchor="w")
        self.lbl_file.grid(row=0, column=1, columnspan=3)

        tk.Label(frm, text="OSC Host:").grid(row=1, column=0)
        self.entry_host = tk.Entry(frm, width=15)
        self.entry_host.insert(0, "127.0.0.1")
        self.entry_host.grid(row=1, column=1)

        tk.Label(frm, text="OSC Port:").grid(row=1, column=2)
        self.entry_port = tk.Entry(frm, width=6)
        self.entry_port.insert(0, "8000")
        self.entry_port.grid(row=1, column=3)

        self.btn_start = tk.Button(frm, text="Start", command=self.start)
        self.btn_start.grid(row=2, column=0)
        self.btn_stop = tk.Button(frm, text="Stop", command=self.stop, state=tk.DISABLED)
        self.btn_stop.grid(row=2, column=1)

        self.lbl_status = tk.Label(frm, text="Status: idle", anchor="w")
        self.lbl_status.grid(row=3, column=0, columnspan=4, sticky="w")

        # polling thread to update status
        self._polling = True
        threading.Thread(target=self._poll_proc, daemon=True).start()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def select_file(self):
        fp = filedialog.askopenfilename(title="Select video file",
                                        filetypes=[("Video files", "*.mp4 *.mov *.avi *.mkv"), ("All files", "*")])
        if fp:
            self.filepath = fp
            self.lbl_file.config(text=os.path.basename(fp))

    def start(self):
        if not self.filepath:
            messagebox.showwarning("No file", "Please select a video file first")
            return
        if self.proc and self.proc.poll() is None:
            messagebox.showinfo("Already running", "Processing is already running")
            return

        host = self.entry_host.get().strip() or "127.0.0.1"
        port = int(self.entry_port.get().strip() or 8000)

        cmd = [sys.executable, MAIN_PY, "--video", self.filepath, "--host", host, "--port", str(port)]
        try:
            self.proc = subprocess.Popen(cmd)
        except Exception as e:
            messagebox.showerror("Failed to start", str(e))
            return

        self.lbl_status.config(text=f"Status: running (pid {self.proc.pid})")
        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)

    def stop(self):
        if not self.proc or self.proc.poll() is not None:
            self.lbl_status.config(text="Status: idle")
            self.btn_start.config(state=tk.NORMAL)
            self.btn_stop.config(state=tk.DISABLED)
            return
        try:
            # try graceful interrupt first
            self.proc.send_signal(signal.SIGINT)
            # wait briefly
            for _ in range(20):
                if self.proc.poll() is not None:
                    break
                time.sleep(0.1)
            if self.proc.poll() is None:
                self.proc.terminate()
        except Exception:
            try:
                self.proc.kill()
            except Exception:
                pass

        self.lbl_status.config(text="Status: stopped")
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)

    def _poll_proc(self):
        while self._polling:
            if self.proc:
                if self.proc.poll() is None:
                    self.lbl_status.config(text=f"Status: running (pid {self.proc.pid})")
                else:
                    self.lbl_status.config(text="Status: idle")
                    self.btn_start.config(state=tk.NORMAL)
                    self.btn_stop.config(state=tk.DISABLED)
                    self.proc = None
            time.sleep(0.5)

    def _on_close(self):
        self._polling = False
        try:
            if self.proc and self.proc.poll() is None:
                self.proc.terminate()
        except Exception:
            pass
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == '__main__':
    GuiUploader().run()
