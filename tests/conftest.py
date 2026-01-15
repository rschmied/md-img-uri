"""Pytest fixtures for md-img-uri tests."""

import pytest
from PIL import Image


@pytest.fixture
def small_png(tmp_path):
    """Create 10x10 blue PNG."""
    img = Image.new("RGB", (10, 10), color="blue")
    path = tmp_path / "small.png"
    img.save(path)
    return path


@pytest.fixture
def large_png(tmp_path):
    """Create 200x100 green PNG."""
    img = Image.new("RGB", (200, 100), color="green")
    path = tmp_path / "large.png"
    img.save(path)
    return path


@pytest.fixture
def svg_viewbox(tmp_path):
    """SVG with viewBox."""
    content = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="40"/></svg>'
    path = tmp_path / "viewbox.svg"
    path.write_text(content)
    return path


@pytest.fixture
def svg_explicit(tmp_path):
    """SVG with explicit width/height."""
    content = '<svg xmlns="http://www.w3.org/2000/svg" width="150" height="150"><circle cx="75" cy="75" r="60"/></svg>'
    path = tmp_path / "explicit.svg"
    path.write_text(content)
    return path
