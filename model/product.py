class Product:
    def __init__(self, id, isOwner, name, description, main_img):
        self.id = id
        self.isOwner = isOwner
        self.name = name
        self.description = description
        self.main_img = main_img
        self.images = []
        self.stock = {'key' : 'value'}
        self.price = {}

    def add_image(self, image):
        self.images.append(image)
    
    def add_stock(self, store_id, stock):
        #self.stock[str(store_id)] = stock
        self.stock['test'] = 5
