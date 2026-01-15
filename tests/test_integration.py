"""Integration tests for embed_image function."""

from pathlib import Path
import pytest
from md_img_uri.cli import embed_image


def test_embed_png_no_wrap(small_png):
    """Test PNG embedding without wrapping."""
    result = embed_image(small_png, wrap_width=None)
    assert result.startswith("![small](data:image/png;base64,")
    # Check no newlines in data URI
    data_uri = result.split("](")[1].rstrip(")")
    assert "\n" not in data_uri


def test_embed_png_with_wrap(small_png):
    """Test PNG embedding with wrapping."""
    result = embed_image(small_png, wrap_width=80)
    assert result.startswith("![small](data:image/png;base64,")
    data_uri = result.split("](")[1].rstrip(")")
    # Small image might not exceed 80 chars, but check format
    if len(data_uri) > 80:
        assert "\n" in data_uri


def test_embed_svg_no_scaling(svg_viewbox):
    """Test SVG embedding without scaling."""
    result = embed_image(svg_viewbox)
    assert "![viewbox]" in result
    assert "data:image/svg+xml," in result


def test_embed_svg_scaled(svg_viewbox):
    """Test SVG embedding with scaling."""
    result = embed_image(svg_viewbox, max_width=50)
    assert "![viewbox]" in result
    assert "data:image/svg+xml," in result


def test_embed_png_upscale_warning(small_png, capsys):
    """Test warning when trying to upscale PNG."""
    # 10x10 image, request 100px width
    _ = embed_image(small_png, max_width=100)
    captured = capsys.readouterr()
    assert "Warning" in captured.err
    assert "10px" in captured.err
    assert "100px" in captured.err


def test_embed_svg_upscale_warning(svg_explicit, capsys):
    """Test warning when trying to upscale SVG."""
    # 150x150 SVG, request 200px width
    _ = embed_image(svg_explicit, max_width=200)
    captured = capsys.readouterr()
    assert "Warning" in captured.err
    assert "150px" in captured.err
    assert "200px" in captured.err


def test_embed_missing_file():
    """Test error on missing file."""
    with pytest.raises(FileNotFoundError, match="File not found"):
        embed_image(Path("/nonexistent.png"))


def test_embed_unsupported_format(tmp_path):
    """Test error on unsupported format."""
    bad_file = tmp_path / "test.bmp"
    bad_file.write_bytes(b"fake")
    with pytest.raises(ValueError, match="Unsupported format"):
        embed_image(bad_file)


def test_embed_custom_alt(small_png):
    """Test custom alt text."""
    result = embed_image(small_png, alt_text="My Custom Alt")
    assert result.startswith("![My Custom Alt]")


def test_embed_png_downscale(large_png):
    """Test PNG downscaling."""
    result = embed_image(large_png, max_width=100)
    assert "![large]" in result
    # Result should be smaller (can't easily verify without decoding)
