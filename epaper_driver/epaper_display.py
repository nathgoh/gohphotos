from io import BytesIO
import epaper_driver.epaper_7in3 as epaper_7in3

from PIL import Image, ImageOps




class EPD:
    def __init__(self):

        self._epd = epaper_7in3.EPD()
        self._epd.init()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.sleep()

    def show(self, image_bytes: bytes) -> None:
        image: Image = Image.open(BytesIO(image_bytes))
        image: Image = ImageOps.fit(image, (800, 480), method=Image.Resampling.LANCZOS)
        self._epd.display(self._epd.get_buffer(image))
        self.sleep()

    def sleep(self) -> None:
        self._epd.sleep()

    def clear(self) -> None:
        self._epd.clear()
