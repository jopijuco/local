class Product:
    def __init__(self, id, isOwner, name, description, main_img):
        self.id = id
        self.isOwner = isOwner
        self.name = name
        self.description = description
        self.main_img = main_img
        self.images = []
        self.stock = {}
        self.price = {}

    def add_image(self, image):
        self.images.append(image)
    
    def add_stock(self, store_id, stock):
        self.stock[store_id] = stock
    
    def add_price(self, store_id, price):
        self.price[store_id] = price

class Product_shop:
    def __init__(self, id, name, description, main_img, price):
        self.id = id
        self.name = name
        self.description = description
        self.main_img = main_img
        self.price = price
    
    
     