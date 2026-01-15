"""Tests for raster image scaling."""

import io
from PIL import Image
from md_img_uri.cli import scale_raster


def test_scale_raster_downscale():
    """Test raster downscaling preserves aspect ratio."""
    # Create 200x100 image
    img = Image.new("RGB", (200, 100), color="red")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    img_bytes = buf.getvalue()

    result_bytes, upscaling = scale_raster(img_bytes, 100, "image/png")
    assert not upscaling

    result_img = Image.open(io.BytesIO(result_bytes))
    assert result_img.width == 100
    assert result_img.height == 50


def test_scale_raster_upscale_blocked(capsys):
    """Test upscaling is blocked for raster images."""
    # Create 50x50 image
    img = Image.new("RGB", (50, 50), color="blue")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    img_bytes = buf.getvalue()

    result_bytes, upscaling = scale_raster(img_bytes, 100, "image/png")
    assert upscaling
    assert result_bytes == img_bytes  # Unchanged

    # Check warning printed
    captured = capsys.readouterr()
    assert "Warning" in captured.err
    assert "50px" in captured.err
    assert "100px" in captured.err


def test_scale_raster_exact_size():
    """Test exact size match returns original."""
    img = Image.new("RGB", (100, 100), color="green")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    img_bytes = buf.getvalue()

    result_bytes, upscaling = scale_raster(img_bytes, 100, "image/png")
    assert not upscaling
    assert result_bytes == img_bytes  # No reencoding


def test_scale_raster_jpeg():
    """Test scaling JPEG format."""
    img = Image.new("RGB", (200, 150), color="yellow")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    img_bytes = buf.getvalue()

    result_bytes, upscaling = scale_raster(img_bytes, 100, "image/jpeg")
    assert not upscaling

    result_img = Image.open(io.BytesIO(result_bytes))
    assert result_img.width == 100
    assert result_img.height == 75
