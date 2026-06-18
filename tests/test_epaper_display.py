import io
import pytest
from PIL import Image
from epaper_display import _prepare_image

def _make_jpeg_bytes(width: int = 1920, height: int = 1080) -> bytes:
    img = Image.new("RGB", (width, height), color=(100, 149, 237))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()

def test_prepare_image_output_size():
    result = _prepare_image(_make_jpeg_bytes())
    assert result.size == (800, 480)

def test_prepare_image_mode_is_rgb():
    result = _prepare_image(_make_jpeg_bytes())
    assert result.mode == "RGB"

def test_prepare_image_pixels_are_palette_colors():
    """Every pixel must be one of the 7 ACeP palette colors."""
    PALETTE = {
        (0, 0, 0),
        (255, 255, 255),
        (255, 255, 0),
        (255, 0, 0),
        (255, 128, 0),
        (0, 0, 255),
        (0, 255, 0),
    }
    result = _prepare_image(_make_jpeg_bytes())
    unique = set(result.get_flattened_data())
    assert unique.issubset(PALETTE), f"Unexpected colors: {unique - PALETTE}"

def test_prepare_image_portrait_input():
    """Portrait images (taller than wide) are still cropped to 800x480."""
    result = _prepare_image(_make_jpeg_bytes(width=1080, height=1920))
    assert result.size == (800, 480)
