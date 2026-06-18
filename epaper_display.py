from io import BytesIO

from PIL import Image, ImageOps

try:
    from waveshare_epd import epd7in3f
    _HAS_HARDWARE = True
except ImportError:
    _HAS_HARDWARE = False

# ACeP 7-color palette — ordered by display color code (0x0–0x6)
# Index: 0=BLACK 1=WHITE 2=YELLOW 3=RED 4=ORANGE 5=BLUE 6=GREEN
_PALETTE_RGB = [
    0,   0,   0,    # BLACK   0x0
    255, 255, 255,  # WHITE   0x1
    255, 255, 0,    # YELLOW  0x2
    255, 0,   0,    # RED     0x3
    255, 128, 0,    # ORANGE  0x4
    0,   0,   255,  # BLUE    0x5
    0,   255, 0,    # GREEN   0x6
]
_PALETTE_RGB += [0] * (256 * 3 - len(_PALETTE_RGB))

_PALETTE_IMAGE = Image.new("P", (1, 1))
_PALETTE_IMAGE.putpalette(_PALETTE_RGB)


def _prepare_image(image_bytes: bytes) -> Image.Image:
    img = Image.open(BytesIO(image_bytes)).convert("RGB")
    img = ImageOps.fit(img, (800, 480), method=Image.Resampling.LANCZOS)
    img = img.quantize(palette=_PALETTE_IMAGE, dither=Image.Dither.FLOYDSTEINBERG)
    return img.convert("RGB")


class EpaperDisplay:
    def __init__(self):
        if not _HAS_HARDWARE:
            raise RuntimeError(
                "waveshare_epd not available — are you running on a Raspberry Pi?"
            )
        self._epd = epd7in3f.EPD()
        self._epd.init()

    def show(self, image_bytes: bytes) -> None:
        img = _prepare_image(image_bytes)
        self._epd.display(self._epd.getbuffer(img))
        self.sleep()

    def sleep(self) -> None:
        self._epd.sleep()

    def clear(self) -> None:
        self._epd.Clear()
