"""CLI tool to embed images into Markdown as data URIs."""

import argparse
import base64
import io
import re
import sys
from pathlib import Path
from urllib.parse import quote

from PIL import Image


MIME_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".svg": "image/svg+xml",
}


def wrap_base64(encoded: str, width: int = 80) -> str:
    """Wrap base64 string into multiple lines.

    Args:
        encoded: Base64-encoded string
        width: Max characters per line

    Returns:
        Wrapped string with newlines
    """
    lines = [encoded[i : i + width] for i in range(0, len(encoded), width)]
    return "\n".join(lines)


def get_svg_width(svg_content: str) -> int | None:
    """Extract width from SVG content.

    Args:
        svg_content: SVG markup

    Returns:
        Width in pixels, or None if not determinable
    """
    # Try explicit width attribute
    width_match = re.search(r'width=["\'](\d+(?:\.\d+)?)', svg_content)
    if width_match:
        return int(float(width_match.group(1)))

    # Try viewBox
    viewbox_match = re.search(
        r'viewBox=["\']([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)["\']', svg_content
    )
    if viewbox_match:
        return int(float(viewbox_match.group(3)))

    return None


def scale_svg(svg_content: str, max_width: int) -> tuple[str, bool]:
    """Inject width/height attributes into SVG to scale it.

    Args:
        svg_content: Original SVG markup
        max_width: Target width in pixels

    Returns:
        Tuple of (modified SVG, upscaling_attempted)
    """
    # Detect original width
    orig_width = get_svg_width(svg_content)
    upscaling = False

    if orig_width and max_width > orig_width:
        upscaling = True
        # Don't scale, return original
        return svg_content, upscaling

    # Parse viewBox to get aspect ratio
    viewbox_match = re.search(
        r'viewBox=["\']([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)["\']', svg_content
    )

    if viewbox_match:
        vb_width = float(viewbox_match.group(3))
        vb_height = float(viewbox_match.group(4))
        aspect_ratio = vb_height / vb_width
        target_height = int(max_width * aspect_ratio)
    else:
        # No viewBox; try to extract width/height
        width_match = re.search(r'width=["\']([\d.]+)["\']', svg_content)
        height_match = re.search(r'height=["\']([\d.]+)["\']', svg_content)

        if width_match and height_match:
            orig_width = float(width_match.group(1))
            orig_height = float(height_match.group(1))
            aspect_ratio = orig_height / orig_width
            target_height = int(max_width * aspect_ratio)
        else:
            # Fallback: square aspect ratio
            target_height = max_width

    # Inject or replace width/height in opening <svg> tag
    svg_content = re.sub(r'(<svg[^>]*)\s+width=["\'][\d.]+["\']', r"\1", svg_content)
    svg_content = re.sub(r'(<svg[^>]*)\s+height=["\'][\d.]+["\']', r"\1", svg_content)
    svg_content = re.sub(
        r"(<svg[^>]*)(>)",
        rf'\1 width="{max_width}" height="{target_height}"\2',
        svg_content,
        count=1,
    )

    return svg_content, upscaling


def scale_raster(img_bytes: bytes, max_width: int, mime: str) -> tuple[bytes, bool]:
    """Scale raster image (PNG/JPEG/GIF) using Pillow.

    Args:
        img_bytes: Original image bytes
        max_width: Target width in pixels
        mime: MIME type for output format

    Returns:
        Tuple of (scaled image bytes, upscaling_attempted)
    """
    img = Image.open(io.BytesIO(img_bytes))

    upscaling = False

    # Detect upscaling attempt
    if img.width < max_width:
        upscaling = True
        print(
            f"Warning: Image is {img.width}px wide but --max-width is {max_width}px. "
            f"Keeping original size to avoid upscaling.",
            file=sys.stderr,
        )
        return img_bytes, upscaling

    # Skip if already exact size
    if img.width == max_width:
        return img_bytes, upscaling

    # Calculate new dimensions preserving aspect ratio
    aspect_ratio = img.height / img.width
    new_height = int(max_width * aspect_ratio)

    # Resize with high-quality resampling
    img_resized = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

    # Encode back to bytes
    output = io.BytesIO()
    format_map = {"image/png": "PNG", "image/jpeg": "JPEG", "image/gif": "GIF"}
    img_format = format_map.get(mime, "PNG")
    img_resized.save(output, format=img_format)

    return output.getvalue(), upscaling


def embed_image(
    path: Path,
    alt_text: str | None = None,
    max_width: int | None = None,
    wrap_width: int | None = None,
) -> str:
    """Convert image file to data URI markdown line.

    Args:
        path: Path to image file
        alt_text: Optional alt text; defaults to filename stem
        max_width: Optional max width in pixels (scales image)
        wrap_width: Wrap base64 output at width chars (None = no wrap)

    Returns:
        Markdown image line with embedded data URI
    """
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    suffix = path.suffix.lower()
    if suffix not in MIME_TYPES:
        supported = ", ".join(MIME_TYPES.keys())
        raise ValueError(f"Unsupported format: {suffix}. Supported: {supported}")

    mime = MIME_TYPES[suffix]
    alt = alt_text or path.stem

    if suffix == ".svg":
        # SVG: URL-encode
        svg_content = path.read_text(encoding="utf-8")

        # Scale if requested
        if max_width:
            svg_content, upscaling = scale_svg(svg_content, max_width)
            if upscaling:
                orig_width = get_svg_width(path.read_text(encoding="utf-8"))
                print(
                    f"Warning: SVG is {orig_width}px wide but --max-width is {max_width}px. "
                    f"Keeping original size to avoid upscaling.",
                    file=sys.stderr,
                )

        encoded = quote(svg_content)
        data_uri = f"data:{mime},{encoded}"
    else:
        # PNG/JPEG/GIF: base64
        img_bytes = path.read_bytes()

        # Scale if requested
        if max_width:
            img_bytes, _ = scale_raster(img_bytes, max_width, mime)
            # Warning already printed in scale_raster()

        encoded = base64.b64encode(img_bytes).decode("ascii")

        # Wrap base64 output
        if wrap_width is not None:
            encoded = wrap_base64(encoded, wrap_width)

        data_uri = f"data:{mime};base64,{encoded}"

    return f"![{alt}]({data_uri})"


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Embed images into Markdown as data URIs"
    )
    parser.add_argument("file", type=Path, help="Image file to embed")
    parser.add_argument("--alt", help="Alt text (defaults to filename stem)")
    parser.add_argument(
        "--max-width",
        type=int,
        dest="max_width",
        help="Scale image to max width in pixels (preserves aspect ratio, no upscaling)",
    )
    parser.add_argument(
        "--wrap",
        type=int,
        nargs="?",
        const=80,
        metavar="WIDTH",
        help="Wrap base64 at WIDTH chars (default 80 when flag used, min 40)",
    )

    args = parser.parse_args()

    # Validate wrap width
    if args.wrap is not None and (args.wrap < 40 or args.wrap > sys.maxsize):
        parser.error("--wrap WIDTH must be between 40 and sys.maxsize")

    try:
        markdown = embed_image(
            args.file,
            args.alt,
            max_width=args.max_width,
            wrap_width=args.wrap,
        )
        print(markdown)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
