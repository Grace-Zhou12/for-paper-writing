#!/usr/bin/env python3
"""
Photo File Tagger and Organizer
================================
A tool for photographers to tag files and automatically organize them
into corresponding folders based on their tags.

Supported file formats:
  Images : jpg, jpeg, png, bmp, gif, tiff, tif, webp, heic, heif
  RAW    : cr2, cr3, nef, arw, orf, rw2, dng, raf, pef, srw
  Video  : mp4, mov, avi, mkv, wmv
  Other  : psd, ai, svg, pdf

Usage:
  python photo_tagger.py          # Launch GUI
  python photo_tagger.py --cli    # Launch CLI mode
"""

import os
import shutil
import json
import argparse
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SUPPORTED_EXTENSIONS = {
    "images": [
        ".jpg", ".jpeg", ".png", ".bmp", ".gif",
        ".tiff", ".tif", ".webp", ".heic", ".heif",
    ],
    "raw": [
        ".cr2", ".cr3", ".nef", ".arw", ".orf",
        ".rw2", ".dng", ".raf", ".pef", ".srw",
    ],
    "video": [".mp4", ".mov", ".avi", ".mkv", ".wmv"],
    "other": [".psd", ".ai", ".svg", ".pdf"],
}

ALL_EXTENSIONS = [ext for group in SUPPORTED_EXTENSIONS.values() for ext in group]

TAG_RECORD_FILE = "tag_records.json"

# ---------------------------------------------------------------------------
# Core helpers (no GUI dependency)
# ---------------------------------------------------------------------------


def is_supported_file(filepath: str) -> bool:
    """Return True if *filepath* has a supported extension."""
    return Path(filepath).suffix.lower() in ALL_EXTENSIONS


def load_tag_records(record_path: str) -> dict:
    """Load existing tag records from a JSON file.

    Returns a dict mapping absolute file paths to lists of tags.
    """
    if os.path.isfile(record_path):
        with open(record_path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    return {}


def save_tag_records(records: dict, record_path: str) -> None:
    """Persist *records* to a JSON file."""
    with open(record_path, "w", encoding="utf-8") as fh:
        json.dump(records, fh, ensure_ascii=False, indent=2)


def tag_and_move_file(
    filepath: str,
    tags: list[str],
    dest_root: str,
    *,
    copy: bool = False,
    record_path: str | None = None,
) -> dict[str, str]:
    """Tag a file and move/copy it into per‑tag sub‑folders under *dest_root*.

    Parameters
    ----------
    filepath : str
        Absolute or relative path to the source file.
    tags : list[str]
        One or more tag strings.
    dest_root : str
        Root directory where tag folders will be created.
    copy : bool
        If True the file is **copied** into every tag folder and the
        original file is preserved.  If False (default) the file is
        **moved** into the first tag's folder; subsequent tags receive
        copies from that new location.
    record_path : str | None
        Path to the JSON record file.  ``None`` disables recording.

    Returns
    -------
    dict[str, str]
        Mapping ``{tag: destination_path}`` for every tag processed.
    """
    filepath = os.path.abspath(filepath)
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    if not tags:
        raise ValueError("At least one tag must be provided.")

    sanitized_tags = [t.strip() for t in tags if t.strip()]
    if not sanitized_tags:
        raise ValueError("At least one non‑empty tag must be provided.")

    dest_root = os.path.abspath(dest_root)
    results: dict[str, str] = {}

    for idx, tag in enumerate(sanitized_tags):
        tag_dir = os.path.join(dest_root, tag)
        os.makedirs(tag_dir, exist_ok=True)
        dest_path = os.path.join(tag_dir, os.path.basename(filepath))

        # Avoid overwriting – append a counter when a name collision occurs.
        if os.path.exists(dest_path):
            stem = Path(dest_path).stem
            suffix = Path(dest_path).suffix
            counter = 1
            while os.path.exists(dest_path):
                dest_path = os.path.join(tag_dir, f"{stem}_{counter}{suffix}")
                counter += 1

        # When copy=True every tag gets a copy.  When copy=False the
        # first tag (idx==0) receives a move; later tags copy from the
        # moved location so the file still ends up in all tag folders.
        if copy or idx > 0:
            shutil.copy2(filepath, dest_path)
        else:
            shutil.move(filepath, dest_path)
            # Update filepath so subsequent copies refer to the new location.
            filepath = dest_path

        results[tag] = dest_path

    # Persist record
    if record_path is not None:
        records = load_tag_records(record_path)
        for tag, dest in results.items():
            records.setdefault(dest, [])
            if tag not in records[dest]:
                records[dest].append(tag)
        save_tag_records(records, record_path)

    return results


# ---------------------------------------------------------------------------
# CLI interface
# ---------------------------------------------------------------------------


def cli_main() -> None:
    """Simple interactive command‑line interface."""
    print("=" * 50)
    print("  Photo File Tagger & Organizer (CLI)")
    print("=" * 50)

    while True:
        filepath = input("\nEnter file path (or 'quit' to exit): ").strip()
        if filepath.lower() in ("quit", "exit", "q"):
            break

        if not os.path.isfile(filepath):
            print(f"  [Error] File not found: {filepath}")
            continue

        if not is_supported_file(filepath):
            print(f"  [Warning] Unsupported format: {Path(filepath).suffix}")
            proceed = input("  Continue anyway? (y/n): ").strip().lower()
            if proceed != "y":
                continue

        tags_input = input("Enter tags (comma‑separated): ").strip()
        tags = [t.strip() for t in tags_input.split(",") if t.strip()]
        if not tags:
            print("  [Error] No valid tags provided.")
            continue

        dest_root = input(
            "Destination root folder (default: current directory): "
        ).strip()
        if not dest_root:
            dest_root = os.getcwd()

        copy_input = input("Copy file instead of move? (y/n, default: n): ").strip()
        use_copy = copy_input.lower() == "y"

        record_path = os.path.join(dest_root, TAG_RECORD_FILE)

        try:
            results = tag_and_move_file(
                filepath, tags, dest_root, copy=use_copy, record_path=record_path
            )
            for tag, dest in results.items():
                print(f"  [OK] Tag '{tag}' -> {dest}")
        except Exception as exc:
            print(f"  [Error] {exc}")

    print("\nGoodbye!")


# ---------------------------------------------------------------------------
# GUI interface (tkinter)
# ---------------------------------------------------------------------------


def gui_main() -> None:
    """Launch a tkinter‑based graphical interface."""
    try:
        import tkinter as tk
        from tkinter import filedialog, messagebox
    except ImportError:
        print("tkinter is not available. Falling back to CLI mode.")
        cli_main()
        return

    # Build extension filter tuples for the file dialog.
    filetypes = [("All supported files", " ".join(f"*{e}" for e in ALL_EXTENSIONS))]
    for group_name, exts in SUPPORTED_EXTENSIONS.items():
        filetypes.append(
            (group_name.capitalize(), " ".join(f"*{e}" for e in exts))
        )
    filetypes.append(("All files", "*.*"))

    # --- Application window ------------------------------------------------
    root = tk.Tk()
    root.title("Photo File Tagger & Organizer")
    root.geometry("640x480")
    root.minsize(480, 360)

    # Variables
    selected_files: list[str] = []
    dest_var = tk.StringVar(value=os.getcwd())
    copy_var = tk.BooleanVar(value=False)

    # --- Widgets -----------------------------------------------------------
    frame_top = tk.Frame(root, padx=10, pady=5)
    frame_top.pack(fill=tk.X)

    tk.Label(frame_top, text="Selected files:").pack(anchor=tk.W)
    file_listbox = tk.Listbox(frame_top, height=8, selectmode=tk.EXTENDED)
    file_listbox.pack(fill=tk.X, pady=(0, 5))

    def browse_files() -> None:
        paths = filedialog.askopenfilenames(
            title="Select files to tag", filetypes=filetypes
        )
        if paths:
            selected_files.clear()
            file_listbox.delete(0, tk.END)
            for p in paths:
                selected_files.append(p)
                file_listbox.insert(tk.END, p)

    tk.Button(frame_top, text="Browse Files…", command=browse_files).pack(
        anchor=tk.W
    )

    # Tags
    frame_mid = tk.Frame(root, padx=10, pady=5)
    frame_mid.pack(fill=tk.X)

    tk.Label(frame_mid, text="Tags (comma‑separated):").pack(anchor=tk.W)
    tag_entry = tk.Entry(frame_mid)
    tag_entry.pack(fill=tk.X, pady=(0, 5))

    # Destination folder
    frame_dest = tk.Frame(root, padx=10, pady=5)
    frame_dest.pack(fill=tk.X)

    tk.Label(frame_dest, text="Destination root folder:").pack(anchor=tk.W)
    dest_entry = tk.Entry(frame_dest, textvariable=dest_var)
    dest_entry.pack(fill=tk.X, side=tk.LEFT, expand=True, pady=(0, 5))

    def browse_dest() -> None:
        d = filedialog.askdirectory(title="Select destination folder")
        if d:
            dest_var.set(d)

    tk.Button(frame_dest, text="Browse…", command=browse_dest).pack(
        side=tk.LEFT, padx=(5, 0)
    )

    # Options
    frame_opt = tk.Frame(root, padx=10, pady=5)
    frame_opt.pack(fill=tk.X)
    tk.Checkbutton(
        frame_opt, text="Copy files (keep originals)", variable=copy_var
    ).pack(anchor=tk.W)

    # Execute
    frame_bot = tk.Frame(root, padx=10, pady=10)
    frame_bot.pack(fill=tk.X)

    def execute() -> None:
        if not selected_files:
            messagebox.showwarning("No files", "Please select files first.")
            return

        tags_text = tag_entry.get().strip()
        tags = [t.strip() for t in tags_text.split(",") if t.strip()]
        if not tags:
            messagebox.showwarning("No tags", "Please enter at least one tag.")
            return

        dest = dest_var.get().strip()
        if not dest:
            messagebox.showwarning(
                "No destination", "Please choose a destination folder."
            )
            return

        record_path = os.path.join(dest, TAG_RECORD_FILE)
        success_count = 0
        errors: list[str] = []

        for fpath in list(selected_files):
            try:
                tag_and_move_file(
                    fpath,
                    tags,
                    dest,
                    copy=copy_var.get(),
                    record_path=record_path,
                )
                success_count += 1
            except Exception as exc:
                errors.append(f"{fpath}: {exc}")

        msg = f"Processed {success_count} file(s) successfully."
        if errors:
            msg += "\n\nErrors:\n" + "\n".join(errors)
            messagebox.showwarning("Done with errors", msg)
        else:
            messagebox.showinfo("Done", msg)

        # Refresh listbox
        selected_files.clear()
        file_listbox.delete(0, tk.END)

    tk.Button(
        frame_bot, text="Tag & Organize", command=execute, bg="#4CAF50", fg="white"
    ).pack(anchor=tk.E)

    root.mainloop()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Photo File Tagger & Organizer"
    )
    parser.add_argument(
        "--cli", action="store_true", help="Use command‑line interface instead of GUI"
    )
    args = parser.parse_args()

    if args.cli:
        cli_main()
    else:
        gui_main()


if __name__ == "__main__":
    main()
