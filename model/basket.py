class FullBasket:
    def __init__(self):
        self.baskets = []

    def add_basket(self, basket):
        self.baskets.append(basket)

class Basket:
    def __init__(self, store_id, amount):
        self.store_id = store_id
        self.amount = amount
        self.products = []

    def add_product(self, product):
        self.products.append(product)
