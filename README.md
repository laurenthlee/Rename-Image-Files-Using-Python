# Smart Renamer — Easy+

A clean, friendly, cross-platform **bulk file renamer** built with Python + Tkinter.

- ✅ Simple, step-by-step UI
- 🔢 Index styles: **Numbers**, **Letters (A, B, C, …)**, **Roman (I, II, III, …)**, or **No index**
- ↔️ Index **position** (before/after base) + custom **separator**
- 🧮 **Auto-pad** numbers or pick digits manually
- 🗂️ Optional **per-subfolder reset** + sorting (name / modified time / size)
- 🧷 **Auto-resolve conflicts** (“name (1).ext”, “name (2).ext”, …)
- ↩️ **Undo last rename** (session-local)
- 📄 **Export CSV** (original → new mapping)
- 🖱️ Right-click: **Open file** / **Show in folder**
- 💡 Live **Example** shows how names will look
- 🟢 No external dependencies

> **Heads-up:** This README gives you the tour. For full docs, see the [`docs/`](./docs) folder.

---

## Quick start

### Requirements
- **Python 3.8+** (3.10+ recommended)
- Tkinter (bundled with Python on Windows/macOS; on Linux install `python3-tk`)

Linux (Debian/Ubuntu):
```bash
sudo apt-get update
sudo apt-get install -y python3 python3-tk
```

### 2-minute tour
- **Folder** – Choose the folder; optionally include files in subfolders.
- **Naming – Set**:

**Base name**
- **Index type**: Numbers / Letters / Roman / None
- **Position**: Before or After base
- **Separator**: _, -, space, etc.
- **Start value**: 1, A, or I
- **Padding (Numbers)**: Auto or 1–6 digits
- **Case**: unchanged / lower / upper / title
- **Extension**: keep / lower / upper

### The Example line updates live (e.g., Vacation_001.jpg).
- **Options** – Sort order; reset numbering per subfolder; auto-resolve conflicts.
- **Go!** – Click Preview, then Rename. Use Undo to roll back the last batch.
- **Export the mapping via Export CSV**.
- **Right-click** a row to Open file or Show in folder.
