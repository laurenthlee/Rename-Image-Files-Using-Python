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
