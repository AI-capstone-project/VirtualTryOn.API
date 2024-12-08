from pathlib import Path
import sys
PROJECT_ROOT = Path(__file__).absolute().parents[0].absolute()
sys.path.insert(0, str(PROJECT_ROOT))

class ImagePreprocessor:
    def __init__(self, img_width, img_height):
        self.img_width = img_width
        self.img_height = img_height

    def center_crop(self, image):
        """Crops the image to a square based on the smaller dimension."""
        width, height = image.size
        new_edge = min(width, height)
        left = (width - new_edge) // 2
        top = (height - new_edge) // 2
        right = (width + new_edge) // 2
        bottom = (height + new_edge) // 2
        return image.crop((left, top, right, bottom))

    def resize(self, image):
        """Resizes the image to the target dimensions."""
        return image.resize((self.img_width, self.img_height))

    def process_vton_image(self, vton_img):
        """Performs preprocessing specific to vton images."""
        vton_img = self.center_crop(vton_img)
        return self.resize(vton_img)

    def process_garm_image(self, garm_img):
        """Processes garment images."""
        return self.resize(garm_img)
