class Product:
    def __init__(self, id, name, description, price, discount, total, main_img):
        self.id = id
        self.name = name
        self.description = description
        self.price = price
        self.discount = discount
        self.total = total
        self.main_img = main_img
        self.images = []

    def add_image(self, image):
        self.images.append(image)
