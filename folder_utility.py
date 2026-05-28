#!/usr/bin/env python3
"""Recurse through a top-level folder and print each folder, its files, and their sizes."""

import argparse
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


def walk_folder(top, human=True):
    """Recurse through `top`, printing each folder, its files, and their sizes.

    Returns the total number of bytes counted across all readable files.
    """
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


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", nargs="?", default=".",
                        help="top-level folder to scan (default: current directory)")
    parser.add_argument("-b", "--bytes", action="store_true",
                        help="show raw byte counts instead of human-readable sizes")
    args = parser.parse_args(argv)

    if not os.path.isdir(args.folder):
        print(f"error: '{args.folder}' is not a directory", file=sys.stderr)
        return 1

    total = walk_folder(args.folder, human=not args.bytes)
    shown = f"{total} B" if args.bytes else human_readable(total)
    print(f"\nTotal: {shown}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
