"""Tests for base64 wrapping logic."""

from md_img_uri.cli import wrap_base64


def test_wrap_default_80():
    """Test wrapping at default 80 chars."""
    encoded = "A" * 160
    result = wrap_base64(encoded, 80)
    lines = result.split("\n")
    assert len(lines) == 2
    assert all(len(line) == 80 for line in lines)


def test_wrap_custom_width():
    """Test wrapping at custom width."""
    encoded = "B" * 120
    result = wrap_base64(encoded, 40)
    lines = result.split("\n")
    assert len(lines) == 3
    assert all(len(line) == 40 for line in lines)


def test_wrap_uneven():
    """Test wrapping with uneven length."""
    encoded = "C" * 85
    result = wrap_base64(encoded, 80)
    lines = result.split("\n")
    assert len(lines) == 2
    assert len(lines[0]) == 80
    assert len(lines[1]) == 5


def test_wrap_exact():
    """Test wrapping with exact multiple."""
    encoded = "D" * 80
    result = wrap_base64(encoded, 80)
    lines = result.split("\n")
    assert len(lines) == 1
    assert len(lines[0]) == 80
