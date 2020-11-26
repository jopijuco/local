from PIL import Image, ImageOps
from constants import *

class Picture:
    def __init__(self, id, name, thumbnail):
        self.id = id
        self.name = name
        self.thumbnail = thumbnail

    def create_thumbnail(self):
        img = Image.open("static/"+self.name)
        img_thumbnail = ImageOps.fit(img, (IMG_THUMBNAIL_SIZE, IMG_THUMBNAIL_SIZE), centering=(1.0, 0.0))
        destname = 'static/thumbnail_'+self.name
        img_thumbnail.save(destname)
        self.thumbnail = img_thumbnail