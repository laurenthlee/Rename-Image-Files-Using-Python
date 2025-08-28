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
