#!/usr/bin/env python3
"""Recurse through a top-level folder and print each folder, its files, and their sizes."""

import argparse
import csv
import os
import sys


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
    """Recurse through `top`, yielding (folder, filename, size_bytes) rows.

    `size_bytes` is None for files that can't be read.
    """
    for dirpath, _dirnames, filenames in os.walk(top):
        for name in sorted(filenames):
            yield dirpath, name, file_size(os.path.join(dirpath, name))


def print_folder(top, human=True):
    """Print each folder, its files, and their sizes. Returns total bytes."""
    total = 0
    for dirpath, _dirnames, filenames in os.walk(top):
        print(f"\n{dirpath}/")
        if not filenames:
            print("    (no files)")
            continue
        for name in sorted(filenames):
            size = file_size(os.path.join(dirpath, name))
            if size is None:
                print(f"    {name:<40} <unreadable>")
                continue
            total += size
            shown = human_readable(size) if human else f"{size} B"
            print(f"    {name:<40} {shown:>12}")
    return total


def write_csv(top, out_path):
    """Write the scan results to a CSV file. Returns total bytes counted."""
    total = 0
    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["folder", "filename", "size_bytes", "size_human"])
        for folder, name, size in scan_folder(top):
            if size is None:
                writer.writerow([folder, name, "", "unreadable"])
                continue
            total += size
            writer.writerow([folder, name, size, human_readable(size)])
    return total


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", nargs="?", default=".",
                        help="top-level folder to scan (default: current directory)")
    parser.add_argument("-b", "--bytes", action="store_true",
                        help="show raw byte counts instead of human-readable sizes")
    parser.add_argument("-o", "--csv", metavar="PATH",
                        help="write results to a CSV file at PATH")
    args = parser.parse_args(argv)

    if not os.path.isdir(args.folder):
        print(f"error: '{args.folder}' is not a directory", file=sys.stderr)
        return 1

    if args.csv:
        total = write_csv(args.folder, args.csv)
        shown = f"{total} B" if args.bytes else human_readable(total)
        print(f"Wrote results to {args.csv}  (total: {shown})")
        return 0

    total = print_folder(args.folder, human=not args.bytes)
    shown = f"{total} B" if args.bytes else human_readable(total)
    print(f"\nTotal: {shown}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
