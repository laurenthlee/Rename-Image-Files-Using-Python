import os
import re
import csv
import platform
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

APP_TITLE = "Smart Renamer — Easy+"

ILLEGAL_WIN_CHARS = r'[<>:"/\\|?*\x00-\x1F]'

# ---------- helpers (platform open)
def open_in_explorer(path: Path):
    try:
        sysname = platform.system()
        if sysname == "Windows":
            os.startfile(path if path.is_file() else str(path))  # type: ignore
        elif sysname == "Darwin":
            os.system(f'open "{path}"')
        else:
            os.system(f'xdg-open "{path}"')
    except Exception:
        pass

# ---------- helpers (index formats)
def int_to_letters(n: int) -> str:
    """1 -> A, 26 -> Z, 27 -> AA (Excel-style)."""
    s = ""
    while n > 0:
        n, rem = divmod(n - 1, 26)
        s = chr(65 + rem) + s
    return s or "A"

def int_to_roman(n: int) -> str:
    if n <= 0 or n >= 4000:
        return str(n)
    vals = [
        (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
        (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
        (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"),
    ]
    out = []
    for v, sym in vals:
        while n >= v:
            out.append(sym)
            n -= v
    return "".join(out)

class EasyPlusRenamer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1060x660")
        self.minsize(980, 600)

        # ---- state
        self.folder_var = tk.StringVar()
        self.base_var = tk.StringVar()
        self.include_sub_var = tk.BooleanVar(value=False)

        self.sort_var = tk.StringVar(value="Name (A→Z)")
        self.reset_per_folder_var = tk.BooleanVar(value=False)
        self.auto_resolve_var = tk.BooleanVar(value=True)

        # indexing options
        self.index_type_var = tk.StringVar(value="Numbers")  # Numbers | Letters | Roman | None
        self.index_pos_var = tk.StringVar(value="After base")  # Before base | After base
        self.sep_var = tk.StringVar(value="_")
        self.start_var = tk.IntVar(value=1)
        self.pad_mode_var = tk.StringVar(value="Auto")  # Auto or digits for Numbers

        # case / ext
        self.case_var = tk.StringVar(value="unchanged")  # unchanged|lower|upper|title
        self.ext_mode_var = tk.StringVar(value="keep")   # keep|lower|upper

        # sample + progress
        self.sample_var = tk.StringVar(value="Example: (choose a folder)")
        self.progress_var = tk.DoubleVar(value=0)
        self.status_var = tk.StringVar(value="Ready.")

        # caches
        self.preview_rows = []     # dicts: old_path, new_name, target_path, status
        self.last_rename_map = []  # list[(dst, src)] for undo

        self._build_ui()
        self._bind_events()
        self._log("Ready.\n")

    # ---------- UI
    def _build_ui(self):
        # comfy scaling
        try:
            self.tk.call("tk", "scaling", 1.25)
        except Exception:
            pass

        # main layout: left controls / right preview
        root = ttk.Frame(self, padding=14)
        root.pack(fill="both", expand=True)

        left = ttk.Frame(root)
        left.pack(side="left", fill="y", padx=(0, 10))

        right = ttk.Frame(root)
        right.pack(side="right", fill="both", expand=True)

        # ---- controls (left)
        lf_folder = ttk.LabelFrame(left, text="Step 1 — Folder")
        lf_folder.pack(fill="x", pady=(0, 10))
        row = ttk.Frame(lf_folder)
        row.pack(fill="x", padx=10, pady=8)
        ttk.Entry(row, textvariable=self.folder_var).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="Browse…", command=self.on_browse).pack(side="left", padx=(8, 0))

        lf_naming = ttk.LabelFrame(left, text="Step 2 — Naming")
        lf_naming.pack(fill="x", pady=(0, 10))
        r1 = ttk.Frame(lf_naming); r1.pack(fill="x", padx=10, pady=(8,4))
        ttk.Label(r1, text="Base name").pack(side="left")
        ttk.Entry(r1, textvariable=self.base_var, width=24).pack(side="left", padx=8)
        ttk.Checkbutton(r1, text="Include subfolders", variable=self.include_sub_var).pack(side="left", padx=(8, 0))

        r2 = ttk.Frame(lf_naming); r2.pack(fill="x", padx=10, pady=4)
        ttk.Label(r2, text="Index type").pack(side="left")
        ttk.Combobox(r2, textvariable=self.index_type_var,
                     values=["Numbers", "Letters", "Roman", "None"],
                     width=12, state="readonly").pack(side="left", padx=6)
        ttk.Label(r2, text="Position").pack(side="left", padx=(8, 2))
        ttk.Combobox(r2, textvariable=self.index_pos_var,
                     values=["After base","Before base"], width=12, state="readonly").pack(side="left")

        r3 = ttk.Frame(lf_naming); r3.pack(fill="x", padx=10, pady=4)
        ttk.Label(r3, text="Separator").pack(side="left")
        ttk.Entry(r3, textvariable=self.sep_var, width=8).pack(side="left", padx=(6, 16))
        ttk.Label(r3, text="Start # / A / I").pack(side="left")
        ttk.Spinbox(r3, from_=0, to=999999, textvariable=self.start_var, width=8).pack(side="left", padx=(6, 16))
        ttk.Label(r3, text="Padding").pack(side="left")
        ttk.Combobox(r3, textvariable=self.pad_mode_var,
                     values=["Auto","1","2","3","4","5","6"],
                     width=6, state="readonly").pack(side="left")

        r4 = ttk.Frame(lf_naming); r4.pack(fill="x", padx=10, pady=4)
        ttk.Label(r4, text="Case").pack(side="left")
        ttk.Combobox(r4, textvariable=self.case_var,
                     values=["unchanged","lower","upper","title"],
                     width=12, state="readonly").pack(side="left", padx=(6, 16))
        ttk.Label(r4, text="Extension").pack(side="left")
        ttk.Combobox(r4, textvariable=self.ext_mode_var,
                     values=["keep","lower","upper"],
                     width=8, state="readonly").pack(side="left")

        r5 = ttk.Frame(lf_naming); r5.pack(fill="x", padx=10, pady=(6, 2))
        ttk.Label(r5, textvariable=self.sample_var, foreground="#0c5460").pack(side="left")

        lf_options = ttk.LabelFrame(left, text="Step 3 — Options")
        lf_options.pack(fill="x", pady=(0, 10))
        o1 = ttk.Frame(lf_options); o1.pack(fill="x", padx=10, pady=6)
        ttk.Label(o1, text="Sort by").pack(side="left")
        ttk.Combobox(o1, textvariable=self.sort_var,
                     values=["Name (A→Z)", "Modified time (old→new)", "Size (small→large)"],
                     width=28, state="readonly").pack(side="left", padx=6)
        ttk.Checkbutton(o1, text="Reset numbering per subfolder", variable=self.reset_per_folder_var).pack(side="left", padx=(10, 0))

        o2 = ttk.Frame(lf_options); o2.pack(fill="x", padx=10, pady=(0,6))
        ttk.Checkbutton(o2, text="Auto-resolve name conflicts", variable=self.auto_resolve_var).pack(side="left")

        lf_actions = ttk.LabelFrame(left, text="Step 4 — Go!")
        lf_actions.pack(fill="x")
        b = ttk.Frame(lf_actions); b.pack(fill="x", padx=10, pady=8)
        ttk.Button(b, text="🔍 Preview   (Enter)", command=self.on_preview).pack(side="left")
        ttk.Button(b, text="✏️ Rename", command=self.on_rename).pack(side="left", padx=8)
        ttk.Button(b, text="↩ Undo", command=self.on_undo).pack(side="left")
        ttk.Button(b, text="🧹 Clear", command=self.on_clear).pack(side="left", padx=8)
        ttk.Button(b, text="⬇ Export CSV", command=self.on_export_csv).pack(side="left")

        st = ttk.Frame(left); st.pack(fill="x", pady=(10,0))
        self.prog = ttk.Progressbar(st, variable=self.progress_var, mode="determinate")
        self.prog.pack(side="left", fill="x", expand=True)
        ttk.Label(st, textvariable=self.status_var).pack(side="left", padx=8)

        # ---- preview (right)
        mid = ttk.LabelFrame(right, text="Preview", padding=(6,6))
        mid.pack(fill="both", expand=True)

        cols = ("file", "newname", "status")
        self.tree = ttk.Treeview(mid, columns=cols, show="headings", height=18)
        self.tree.heading("file", text="Original File")
        self.tree.heading("newname", text="New Name")
        self.tree.heading("status", text="Status")
        self.tree.column("file", width=430, anchor="w")
        self.tree.column("newname", width=430, anchor="w")
        self.tree.column("status", width=110, anchor="center")
        self.tree.pack(fill="both", expand=True, side="left")

        self.tree.tag_configure("ok", foreground="#155724")
        self.tree.tag_configure("conflict", foreground="#721c24")
        self.tree.tag_configure("skip", foreground="#856404")
        self.tree.tag_configure("row_even", background="#f8f9fa")
        self.tree.tag_configure("row_odd", background="#ffffff")

        vsb = ttk.Scrollbar(mid, orient="vertical", command=self.tree.yview)
        vsb.pack(side="right", fill="y")
        self.tree.configure(yscroll=vsb.set)

        # context menu
        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="Open file", command=self._ctx_open_file)
        self.menu.add_command(label="Show in folder", command=self._ctx_show_in_folder)
        self.tree.bind("<Button-3>", self._show_context)
        self.tree.bind("<Double-1>", lambda e: self._ctx_open_file())

        # ---- log
        bot = ttk.LabelFrame(right, text="Log", padding=(6, 6))
        bot.pack(fill="x", expand=False, pady=(10,0))
        self.log = tk.Text(bot, height=7, wrap="word")
        self.log.pack(fill="both", expand=True)

        # theme tweaks
        style = ttk.Style(self)
        try:
            style.theme_use(style.theme_use())
        except Exception:
            style.theme_use("clam")
        style.configure(".", font=("Segoe UI", 10))
        style.configure("Treeview", rowheight=26)
        style.configure("TButton", padding=(10, 6))
        style.configure("TLabel", padding=(2, 2))

        self._toggle_pad_enable()

    def _bind_events(self):
        self.bind("<Return>", lambda e: self.on_preview())
        # live sample
        for var in (self.folder_var, self.base_var, self.index_type_var, self.index_pos_var,
                    self.sep_var, self.start_var, self.pad_mode_var, self.include_sub_var,
                    self.ext_mode_var, self.case_var):
            var.trace_add("write", lambda *_: self._update_sample())
        self.index_type_var.trace_add("write", lambda *_: self._toggle_pad_enable())

    # ---------- actions
    def on_browse(self):
        folder = filedialog.askdirectory(title="Select a folder")
        if folder:
            self.folder_var.set(folder)
            if not self.base_var.get().strip():
                self.base_var.set(Path(folder).name)
            self._update_sample()

    def on_clear(self):
        self.tree.delete(*self.tree.get_children())
        self.preview_rows.clear()
        self.log.delete("1.0", tk.END)
        self.progress_var.set(0)
        self.status_var.set("Cleared.")
        self._log("Cleared.\n")

    def on_export_csv(self):
        if not self.preview_rows:
            messagebox.showinfo("Export CSV", "Nothing to export. Run Preview first.")
            return
        path = filedialog.asksaveasfilename(
            title="Export mapping to CSV",
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
        )
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["Original", "New Name", "Status"])
            for r in self.preview_rows:
                w.writerow([r["old_path"].name, r["new_name"], r["status"]])
        self._log(f"Exported CSV: {path}\n")
        messagebox.showinfo("Export", "CSV exported.")

    def on_preview(self):
        self.tree.delete(*self.tree.get_children())
        self.preview_rows.clear()
        self.progress_var.set(0)

        folder = Path(self.folder_var.get())
        base = self.base_var.get().strip()

        if not folder.exists():
            messagebox.showerror("Error", f"Folder does not exist:\n{folder}")
            return
        if not base:
            messagebox.showerror("Error", "Base name cannot be empty.")
            return

        pattern_glob = "**/*" if self.include_sub_var.get() else "*"
        items = [p for p in folder.glob(pattern_glob) if p.is_file()]
        if not items:
            self._log(f"No files found in: {folder}\n")
            messagebox.showinfo("Preview", "No files found.")
            return

        # Sort
        sort_mode = self.sort_var.get()
        if sort_mode.startswith("Name"):
            items.sort(key=lambda p: (str(p.parent).lower(), p.name.lower()))
        elif sort_mode.startswith("Modified"):
            items.sort(key=lambda p: (str(p.parent).lower(), p.stat().st_mtime))
        else:
            items.sort(key=lambda p: (str(p.parent).lower(), p.stat().st_size))

        # counters
        start = int(self.start_var.get() or 0)
        per_folder_counter = {}
        global_counter = start

        index_type = self.index_type_var.get()
        pad = self._decide_pad(index_type, start, len(items))

        taken = set()
        total = len(items)
        conflicts = 0

        for idx, p in enumerate(items, start=1):
            parent_key = str(p.parent)
            if self.reset_per_folder_var.get():
                c = per_folder_counter.get(parent_key, start)
                per_folder_counter[parent_key] = c + 1
                seq = c
            else:
                seq = global_counter
                global_counter += 1

            index_token = self._format_index(index_type, seq, pad)

            # build stem
            stem_parts = []
            if self.index_pos_var.get() == "Before base":
                if index_token:
                    stem_parts.append(index_token)
                stem_parts.append(self.base_var.get().strip())
            else:
                stem_parts.append(self.base_var.get().strip())
                if index_token:
                    stem_parts.append(index_token)

            sep = self.sep_var.get()
            stem = sep.join([s for s in stem_parts if s != ""])

            # case transform
            stem = self._apply_case(stem)

            # extension mode
            ext = p.suffix
            if self.ext_mode_var.get() == "lower":
                ext = ext.lower()
            elif self.ext_mode_var.get() == "upper":
                ext = ext.upper()

            new_name = self._sanitize(stem) + ext
            target = p.with_name(new_name)

            status = "OK"
            tag = "ok"
            final_target = target

            if new_name == p.name:
                status, tag = "Skip (same)", "skip"
            else:
                exists_conflict = target.exists() or str(target) in taken
                if exists_conflict:
                    if self.auto_resolve_var.get():
                        final_target = self._auto_resolve(target)
                        new_name = final_target.name
                        status, tag = "OK", "ok"
                    else:
                        status, tag = "Conflict", "conflict"
                        conflicts += 1
                taken.add(str(final_target))

            self.preview_rows.append({
                "old_path": p,
                "new_name": new_name,
                "target_path": final_target,
                "status": status
            })

            self.tree.insert("", "end",
                             values=(p.name, new_name, status),
                             tags=(tag, "row_even" if idx % 2 == 0 else "row_odd"))

            self.progress_var.set((idx/total)*100)

        summary = f"Preview: {len(items)} file(s), {conflicts} conflict(s)."
        self.status_var.set(summary)
        self._log(summary + "\n")
        if conflicts and not self.auto_resolve_var.get():
            self._log("Tip: enable Auto-resolve to avoid manual conflicts.\n")

        self._update_sample(count=len(items))

    def on_rename(self):
        if not self.preview_rows:
            messagebox.showinfo("Rename", "Nothing to rename. Click Preview first.")
            return

        if not self.auto_resolve_var.get():
            conflicts = [r for r in self.preview_rows if r["status"] == "Conflict"]
            if conflicts:
                messagebox.showerror("Conflicts found",
                    "There are name conflicts. Enable Auto-resolve or adjust options, then preview again.")
                return

        to_rename = [r for r in self.preview_rows if r["status"] == "OK"]
        if not to_rename:
            messagebox.showinfo("Rename", "Nothing to do (all rows are Skip).")
            return

        if not messagebox.askyesno("Confirm rename",
                                   f"Proceed to rename {len(to_rename)} file(s)?"):
            return

        ok, fail = 0, 0
        self.last_rename_map.clear()
        total = len(to_rename)

        for i, r in enumerate(to_rename, start=1):
            src: Path = r["old_path"]
            dst: Path = r["target_path"]
            try:
                src.rename(dst)
                ok += 1
                self.last_rename_map.append((dst, src))  # for undo
                self._log(f"Renamed: {src.name} -> {dst.name}\n")
            except PermissionError:
                fail += 1
                self._log(f"[Permission denied] {src}\n")
            except OSError as e:
                fail += 1
                self._log(f"[OS error] {src} -> {dst} :: {e}\n")
            self.progress_var.set((i/total)*100)

        self._log(f"Done. Success: {ok}, Failed: {fail}\n")
        messagebox.showinfo("Rename", f"Finished. Success: {ok}, Failed: {fail}")
        self.status_var.set(f"Rename finished — Success: {ok}, Failed: {fail}")

        self.on_preview()

    def on_undo(self):
        if not self.last_rename_map:
            messagebox.showinfo("Undo", "Nothing to undo.")
            return
        if not messagebox.askyesno("Undo last rename", f"Revert {len(self.last_rename_map)} change(s)?"):
            return
        ok, fail = 0, 0
        for dst, src in reversed(self.last_rename_map):
            try:
                if dst.exists():
                    dst.rename(src)
                    ok += 1
                    self._log(f"Reverted: {dst.name} -> {src.name}\n")
                else:
                    fail += 1
                    self._log(f"[Missing] {dst} (cannot revert)\n")
            except Exception as e:
                fail += 1
                self._log(f"[Undo error] {dst} -> {src} :: {e}\n")
        self._log(f"Undo complete. Success: {ok}, Failed: {fail}\n")
        self.status_var.set(f"Undo complete — Success: {ok}, Failed: {fail}")
        self.on_preview()

    # ---------- helpers
    def _toggle_pad_enable(self):
        # disable padding selection when index != Numbers
        is_numbers = self.index_type_var.get() == "Numbers"
        # find the pad combobox widget by walking children in naming frame
        # (kept simple: enable/disable all comboboxes that have our var)
        for w in self.winfo_children():
            pass  # noop
        # simpler: just store whether to use pad in logic; UI remains visible

    def _format_index(self, index_type: str, seq: int, pad: int) -> str:
        if index_type == "None":
            return ""
        if index_type == "Numbers":
            return str(seq).zfill(pad)
        if index_type == "Letters":
            # seq 0 => A (treat 0 as 1)
            return int_to_letters(max(1, seq))
        if index_type == "Roman":
            return int_to_roman(max(1, seq))
        return str(seq).zfill(pad)

    def _decide_pad(self, index_type: str, start: int, count: int) -> int:
        if index_type != "Numbers":
            return 0
        mode = self.pad_mode_var.get()
        if mode != "Auto":
            try:
                d = int(mode)
                return max(1, min(d, 6))
            except Exception:
                return 2
        # Auto
        end = start + max(count - 1, 0)
        return max(1, min(len(str(end)), 6))

    def _apply_case(self, s: str) -> str:
        mode = self.case_var.get()
        if mode == "lower":
            return s.lower()
        if mode == "upper":
            return s.upper()
        if mode == "title":
            return s.title()
        return s

    def _sanitize(self, name: str) -> str:
        s = re.sub(ILLEGAL_WIN_CHARS, "_", name).strip().rstrip(".")
        return s[:240] or "untitled"

    def _auto_resolve(self, target: Path) -> Path:
        stem, ext = target.stem, target.suffix
        i = 1
        cand = target
        while cand.exists():
            cand = target.with_name(f"{stem} ({i}){ext}")
            i += 1
        return cand

    def _update_sample(self, count: int | None = None):
        folder = self.folder_var.get()
        base = self.base_var.get().strip()
        if not folder:
            self.sample_var.set("Example: (choose a folder)")
            return
        if not base:
            self.sample_var.set("Example: (enter a base name)")
            return

        if count is None:
            count = 120

        index_type = self.index_type_var.get()
        start = int(self.start_var.get() or 0)
        pad = self._decide_pad(index_type, start, count)
        idx = self._format_index(index_type, start, pad)

        parts = []
        if self.index_pos_var.get() == "Before base":
            if idx:
                parts.append(idx)
            parts.append(base)
        else:
            parts.append(base)
            if idx:
                parts.append(idx)

        sep = self.sep_var.get()
        stem = sep.join([p for p in parts if p])

        ext = ".jpg"
        if self.ext_mode_var.get() == "upper":
            ext = ext.upper()
        elif self.ext_mode_var.get() == "lower":
            ext = ext.lower()

        stem = self._apply_case(stem)
        self.sample_var.set(f"Example: {self._sanitize(stem) + ext}")

    def _log(self, msg: str):
        self.log.insert(tk.END, msg)
        self.log.see(tk.END)

    # context
    def _show_context(self, event):
        iid = self.tree.identify_row(event.y)
        if iid:
            self.tree.selection_set(iid)
            self.menu.tk_popup(event.x_root, event.y_root)

    def _selected_path(self) -> Path | None:
        sel = self.tree.selection()
        if not sel:
            return None
        idx = self.tree.index(sel[0])
        if 0 <= idx < len(self.preview_rows):
            return self.preview_rows[idx]["old_path"]
        return None

    def _ctx_open_file(self):
        p = self._selected_path()
        if p and p.exists():
            open_in_explorer(p)

    def _ctx_show_in_folder(self):
        p = self._selected_path()
        if p and p.exists():
            open_in_explorer(p.parent)

    # ---------- main
if __name__ == "__main__":
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)  # crisp on HiDPI (Windows)
    except Exception:
        pass

    app = EasyPlusRenamer()
    app.mainloop()
