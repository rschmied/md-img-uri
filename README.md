# md-img-uri

Embed images into Markdown as data URIs—no external files needed.

## Abstract

`md-img-uri` converts PNG, JPEG, GIF, and SVG images into self-contained Markdown lines using data URIs. Binary formats (PNG/JPEG/GIF) are base64-encoded; SVGs are URL-encoded for smaller output. Useful for portable docs, email-ready Markdown, or single-file distribution.

## Features

**Encoding:**

- Raster formats (PNG/JPEG/GIF): base64 (~33% size increase)
- SVG: URL-encoded (compact, no base64 overhead)

**Image Scaling:**

- Preserves aspect ratio
- Pillow-based resizing for raster, SVG attribute injection for vectors
- Refuses to upscale (warns if `--max-width` > source width)

**Line Wrapping:**

- Default: single-line output (easy piping/parsing)
- `--wrap`: multi-line at 80 chars (or custom width)
- SVGs never wrapped

## Limitations

- Large images → very long lines (base64 inflates ~33%)
- Some Markdown renderers have size limits
- Binary files (PNG/JPEG/GIF) become verbose; prefer SVG when possible

## Installation

```bash
cd md-img-uri
uv sync
.venv/bin/md-img-uri <file>
```

Or install globally:
```bash
uv pip install -e .
md-img-uri <file>
```

## Usage

```bash
md-img-uri <file> [OPTIONS]
```

**Arguments:**
- `<file>`: Image path (`.png`, `.jpg`, `.jpeg`, `.gif`, `.svg`)

**Options:**
- `--alt TEXT`: Alt text (defaults to filename stem)
- `--max-width PX`: Scale to max width in pixels (no upscaling)
- `--wrap [WIDTH]`: Wrap base64 output (default 80 chars, min 40)

**Output:** Markdown image line with embedded data URI → stdout

## Examples

**SVG (URL-encoded, single line by default):**
```bash
$ md-img-uri logo.svg
![logo](data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A//www.w3.org...)
```

**PNG (base64, single line by default):**
```bash
$ md-img-uri screenshot.png
![screenshot](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...very long single line...)
```

**Enable wrapping at 80 chars:**
```bash
$ md-img-uri screenshot.png --wrap
![screenshot](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...
...wrapped across multiple lines at 80 chars...)
```

**Custom wrap width:**
```bash
$ md-img-uri screenshot.png --wrap 120
![screenshot](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...
...wrapped at 120 chars...)
```

**Scale image to 400px width:**
```bash
$ md-img-uri large-photo.jpg --max-width 400
![large-photo](data:image/jpeg;base64,/9j/4AAQSkZJRgABAQ...)
```

**Upscaling attempt (warns and keeps original):**
```bash
$ md-img-uri small-icon.png --max-width 500
Warning: Image is 64px wide but --max-width is 500px. Keeping original size to avoid upscaling.
![small-icon](data:image/png;base64,...)
```

**Custom alt text:**
```bash
$ md-img-uri chart.png --alt "Q4 Revenue Chart"
![Q4 Revenue Chart](data:image/png;base64,iVBORw0KGgo...)
```

**Pipe to file:**
```bash
$ md-img-uri diagram.svg >> report.md
```

## Supported Formats

| Format | Encoding | MIME Type |
|--------|----------|-----------|
| PNG    | base64   | `image/png` |
| JPEG   | base64   | `image/jpeg` |
| GIF    | base64   | `image/gif` |
| SVG    | URL      | `image/svg+xml` |

## Why Data URIs?

- **Portability**: Single file, no broken image links
- **Email/Gist**: Paste Markdown anywhere without hosting images
- **Archival**: Self-contained documentation
- **Offline**: Works without network access

## License

Same as parent project.
