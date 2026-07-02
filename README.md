# folder_utility

Recursively scans a folder and reports every file with its size. For video files it
also reports the **codec** and **resolution** (480p / 720p / 1080p / 4K) and flags
likely **compression candidates** — large files not already encoded in h.265/HEVC — to
help decide what's worth re-compressing on a media server.

Output goes to the console and/or a CSV.

## Requirements

- Python 3.6+
- For codec/resolution: [`pymediainfo`](https://pypi.org/project/pymediainfo/) **plus**
  the native `libmediainfo` library on the host that runs the script.

```bash
pip install -r requirements.txt

# libmediainfo is a system package (not pip):
apt install libmediainfo0v5     # Debian/Ubuntu
brew install mediainfo          # macOS
```

If `pymediainfo`/`libmediainfo` aren't installed, the size scan still works — codec and
resolution are simply left blank.

## Usage

Edit the settings at the top of `folder_utility.py`, then run:

```bash
python folder_utility.py
```

### Settings

| Setting | Default | Description |
|---|---|---|
| `TOP_FOLDER` | `"."` | Top-level folder to scan (recursively). |
| `CSV_OUTPUT` | `"report.csv"` | Path for the CSV report; set to `None` to skip. |
| `PRINT_TO_CONSOLE` | `True` | Also print results to the console. |
| `VIDEO_EXTS` | common video extensions | Which extensions get probed for codec/resolution. |
| `COMPRESSION_MIN_GB` | `24` | Only files larger than this are flagged as candidates. |
| `HEVC_FORMATS` | `HEVC`, `H.265`, … | Codec formats treated as "already compressed". |

## Compression-candidate rule

A file is flagged `*CANDIDATE*` when it is **larger than `COMPRESSION_MIN_GB`** and its
codec is **not** in `HEVC_FORMATS`. A large file with an unknown/unreadable codec is
also flagged, so it gets a look rather than being silently skipped.

## Output

**Console** — files grouped by folder, with size, `codec resolution`, and a
`*CANDIDATE*` marker, followed by a grand total and a candidate count.

**CSV** — columns: `folder, filename, size_bytes, size_human, codec, resolution,
compression_candidate`.
