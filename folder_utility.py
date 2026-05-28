#!/usr/bin/env python3
"""Recurse a top-level folder and report each folder, its files, and their sizes.

Edit the settings below, then run:  python folder_utility.py
"""

import csv
import os

# ---- settings -------------------------------------------------------------
TOP_FOLDER = "."            # top-level folder to scan
CSV_OUTPUT = "report.csv"   # path to write the CSV to (set to None to skip the CSV)
PRINT_TO_CONSOLE = True     # also print results to the console
# ---------------------------------------------------------------------------


def human_readable(size):
    """Convert a byte count into a human-readable string (e.g. 1.5 KB)."""
    for unit in ("B", "KB", "MB", "GB", "TB", "PB"):
        if size < 1024 or unit == "PB":
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024


def file_size(path):
    """Return the size of a file in bytes, or None if it can't be read."""
    try:
        return os.path.getsize(path)
    except OSError:
        return None


def scan_folder(top):
    """Recurse through `top`, returning a list of (folder, filename, size_bytes).

    `size_bytes` is None for files that can't be read.
    """
    rows = []
    for dirpath, _dirnames, filenames in os.walk(top):
        for name in sorted(filenames):
            rows.append((dirpath, name, file_size(os.path.join(dirpath, name))))
    return rows


def print_results(rows):
    """Print each folder, its files, and their sizes."""
    current = None
    for folder, name, size in rows:
        if folder != current:
            print(f"\n{folder}/")
            current = folder
        shown = "<unreadable>" if size is None else human_readable(size)
        print(f"    {name:<40} {shown:>12}")
    total = sum(s for _, _, s in rows if s is not None)
    print(f"\nTotal: {human_readable(total)}")


def write_csv(rows, out_path):
    """Write scan rows to a CSV file with byte and human-readable sizes."""
    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["folder", "filename", "size_bytes", "size_human"])
        for folder, name, size in rows:
            if size is None:
                writer.writerow([folder, name, "", "unreadable"])
            else:
                writer.writerow([folder, name, size, human_readable(size)])


def run(top=TOP_FOLDER, csv_output=CSV_OUTPUT, print_to_console=PRINT_TO_CONSOLE):
    """Scan `top` once, then optionally print and/or write a CSV."""
    rows = scan_folder(top)
    if print_to_console:
        print_results(rows)
    if csv_output:
        write_csv(rows, csv_output)
        print(f"\nWrote CSV to {csv_output}")


if __name__ == "__main__":
    run()
