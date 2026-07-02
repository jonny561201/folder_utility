#!/usr/bin/env python3
"""Recurse a top-level folder and report each folder, its files, and their sizes.

For video files it also reports the codec and resolution (480p/720p/1080p/4K) and
flags likely compression candidates (large files not already in h.265/HEVC), to help
decide what's worth re-compressing on a media server.

Reading codec/resolution needs pymediainfo plus the native libmediainfo on the host
that runs this script:
    pip install pymediainfo
    # and one of:
    apt install libmediainfo0v5     # Debian/Ubuntu
    brew install mediainfo          # macOS
If it isn't installed the size scan still works; codec/resolution are left blank.

Edit the settings below, then run:  python folder_utility.py
"""

import csv
import os

# ---- settings -------------------------------------------------------------
TOP_FOLDER = "."            # top-level folder to scan
CSV_OUTPUT = "report.csv"   # path to write the CSV to (set to None to skip the CSV)
PRINT_TO_CONSOLE = True     # also print results to the console

VIDEO_EXTS = {".mkv", ".mp4", ".m4v", ".avi", ".mov", ".wmv",
              ".ts", ".m2ts", ".flv", ".webm", ".mpg", ".mpeg"}
COMPRESSION_MIN_GB = 24     # only flag files larger than this as candidates
# Codec formats treated as "already compressed" (i.e. not worth re-compressing).
HEVC_FORMATS = {"HEVC", "H.265", "V_MPEGH/ISO/HEVC"}
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


def probe_media(path):
    """Return (codec, width, height) for a video file, or ("", None, None).

    Non-video files (by extension) are skipped without probing. Any failure to import
    pymediainfo or parse the file degrades gracefully to ("", None, None) so one bad
    file - or a host missing libmediainfo - never aborts the scan.
    """
    if os.path.splitext(path)[1].lower() not in VIDEO_EXTS:
        return "", None, None
    try:
        from pymediainfo import MediaInfo

        info = MediaInfo.parse(path)
        for track in info.tracks:
            if track.track_type == "Video":
                return track.format or "", track.width, track.height
    except Exception:
        pass
    return "", None, None


def resolution_label(width, height):
    """Bucket a video into 4K/1080p/720p/480p/SD by width, or "" if unknown.

    Width is more reliable than height for cinematic aspect ratios (e.g. a 4K film may
    be 3840x1600, whose height alone would look like less than 2160p).
    """
    if not width:
        return ""
    if width >= 3840:
        return "4K"
    if width >= 1920:
        return "1080p"
    if width >= 1280:
        return "720p"
    if width >= 640:
        return "480p"
    return "SD"


def is_compression_candidate(size, codec):
    """True if a file is large enough and not already in an h.265/HEVC format.

    A blank/unknown codec on a large file still flags as a candidate - safer to flag it
    for review than to silently skip it.
    """
    if size is None or size <= COMPRESSION_MIN_GB * 1024 ** 3:
        return False
    return codec.upper() not in {f.upper() for f in HEVC_FORMATS}


def scan_folder(top):
    """Recurse through `top`, returning a list of per-file dicts.

    Each dict has: folder, filename, size (bytes or None), codec, resolution, candidate.
    """
    rows = []
    for dirpath, _dirnames, filenames in os.walk(top):
        for name in sorted(filenames):
            path = os.path.join(dirpath, name)
            size = file_size(path)
            codec, width, height = probe_media(path)
            rows.append({
                "folder": dirpath,
                "filename": name,
                "size": size,
                "codec": codec,
                "resolution": resolution_label(width, height),
                "candidate": is_compression_candidate(size, codec),
            })
    return rows


def print_results(rows):
    """Print each folder, its files, sizes, codec/resolution, and candidate flags."""
    current = None
    for row in rows:
        if row["folder"] != current:
            print(f"\n{row['folder']}/")
            current = row["folder"]
        size = row["size"]
        shown = "<unreadable>" if size is None else human_readable(size)
        media = " ".join(p for p in (row["codec"], row["resolution"]) if p)
        marker = "  *CANDIDATE*" if row["candidate"] else ""
        print(f"    {row['filename']:<40} {shown:>12}  {media:<16}{marker}")
    total = sum(r["size"] for r in rows if r["size"] is not None)
    print(f"\nTotal: {human_readable(total)}")

    # Dedicated candidate list, biggest first - the best re-encode targets up top.
    candidates = sorted(
        (r for r in rows if r["candidate"]),
        key=lambda r: r["size"] or 0,
        reverse=True,
    )
    print(f"\nCompression candidates: {len(candidates)}"
          " (largest, non-h.265 files first)")
    for r in candidates:
        media = " ".join(p for p in (r["codec"], r["resolution"]) if p)
        print(f"    {human_readable(r['size']):>10}  {media:<16}  "
              f"{os.path.join(r['folder'], r['filename'])}")


def write_csv(rows, out_path):
    """Write scan rows to a CSV file with sizes, codec, resolution, and candidate flag."""
    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["folder", "filename", "size_bytes", "size_human",
                         "codec", "resolution", "compression_candidate"])
        for row in rows:
            size = row["size"]
            size_bytes = "" if size is None else size
            size_human = "unreadable" if size is None else human_readable(size)
            writer.writerow([row["folder"], row["filename"], size_bytes, size_human,
                             row["codec"], row["resolution"], row["candidate"]])


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
