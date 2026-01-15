"""Tests for SVG parsing and scaling."""

from md_img_uri.cli import get_svg_width, scale_svg


def test_get_svg_width_viewbox():
    """Test extracting width from viewBox."""
    svg = '<svg viewBox="0 0 200 100">...</svg>'
    assert get_svg_width(svg) == 200


def test_get_svg_width_explicit():
    """Test extracting explicit width attribute."""
    svg = '<svg width="150" height="100">...</svg>'
    assert get_svg_width(svg) == 150


def test_get_svg_width_explicit_decimal():
    """Test extracting decimal width."""
    svg = '<svg width="150.5" height="100">...</svg>'
    assert get_svg_width(svg) == 150


def test_get_svg_width_none():
    """Test no width found."""
    svg = "<svg>...</svg>"
    assert get_svg_width(svg) is None


def test_scale_svg_downscale():
    """Test SVG downscaling preserves aspect ratio."""
    svg = '<svg viewBox="0 0 200 100"><rect/></svg>'
    result, upscaling = scale_svg(svg, 100)
    assert not upscaling
    assert 'width="100"' in result
    assert 'height="50"' in result


def test_scale_svg_upscale_blocked():
    """Test upscaling is blocked for SVGs."""
    svg = '<svg width="100" height="100"><circle/></svg>'
    result, upscaling = scale_svg(svg, 200)
    assert upscaling
    assert result == svg  # Unchanged


def test_scale_svg_square_aspect():
    """Test SVG with square viewBox."""
    svg = '<svg viewBox="0 0 100 100"><rect/></svg>'
    result, upscaling = scale_svg(svg, 50)
    assert not upscaling
    assert 'width="50"' in result
    assert 'height="50"' in result
