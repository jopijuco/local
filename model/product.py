class Product:
    def __init__(self, id, isOwner, name, description, main_img):
        self.id = id
        self.isOwner = isOwner
        self.name = name
        self.description = description
        self.main_img = main_img
        self.images = []

    def add_image(self, image):
        self.images.append(image)
