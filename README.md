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

### User Interface
<img width="1050" height="685" alt="image" src="https://github.com/user-attachments/assets/71bd8928-4b61-4c6e-98dd-53f0efdfeaec" />

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

# Packaging (Optional)

You can ship a standalone binary using **PyInstaller**.

## Install PyInstaller
```bash
pip install pyinstaller
```

# Troubleshooting

## Common issues

### “Folder does not exist”
- Check the path. If it’s on a network drive, ensure it’s mounted and you have permissions.

### Nothing appears in Preview
- The folder might be empty or contain only subfolders (no files).
- Confirm **Include subfolders** if your files are nested.

### Permission denied during Rename
- Close files opened in other apps (media players, editors, cloud sync conflicts).
- On Windows, some folders require elevated permissions.

### Undo did not revert a file
- The renamed file has been moved/renamed/deleted after the operation.
- Undo only reverts the **last batch** of renames in the current session.

### Tkinter not found
- Install Tkinter for your distro. Examples:
  - Debian/Ubuntu: `sudo apt-get install python3-tk`
  - Fedora: `sudo dnf install python3-tkinter`
  - Arch: `sudo pacman -S tk`

### Non-ASCII characters look odd
- Ensure your OS and filesystem are using UTF-8 (most modern distros do).
- When exporting CSV, the file is saved as UTF-8.

## Getting help
Please include:
- OS + Python version (`python --version`)
- Steps to reproduce (folder structure, chosen options)
- A copy of the **Log** output

# FAQ

### Does this change file extensions?
Only the **case** of the extension if you choose **lower** or **upper**. The extension itself is preserved.

### Can I remove separators entirely?
Yes—just leave **Separator** empty.

### Can I start at 0 or negative numbers?
Numbers can start at 0. Negative values are allowed but uncommon; results are as-typed.

### Do letters go beyond Z?
Yes. After Z, the sequence continues: `AA, AB, …`.

### How are Roman numerals handled?
Standard subtractive notation up to 3999 (`MMMCMXCIX`). Larger numbers fall back to digits.

### Can I move files to a different folder?
No—this app **renames** only. It keeps files in their current folders.

### Is there a dark mode?
Not yet. It’s on the roadmap.

### Can I rename folders?
No, only files. (Folder rename support may come later.)

### What if a target name already exists?
If **Auto-resolve** is enabled, the app generates `name (1).ext`, `name (2).ext`, …

### What does Undo cover?
Undo reverts the **last rename batch** performed in the current session. Closing the app clears the history.
