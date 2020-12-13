class Basket_Manager():
    def __init__(self):
        self.basket = {}
    
    def get_dict(self):
        return self.basket
    
    def add(self, key, quantity):
        self.basket[key] = quantity
    
    def remove(self, key):
        del self.basket[key]
    
    def total(self, full_basket):
        total = 0
        for b in full_basket.baskets:
            total += float(b.amount)
        return total
    
    def get_store_list(self):
        store_list = []
        for key in self.basket:
            store_list.append(key[1])
        #remove doublon from store_list
        return list(set(store_list))
    
    def empty_basket(self):
        self.basket = {}

#fullBasket = one or more basket (1 basket per store)
class FullBasket:
    def __init__(self):
        self.baskets = []

    def add_basket(self, basket):
        self.baskets.append(basket)

class Basket:
    def __init__(self, store_id, store_name, amount):
        self.store_id = store_id
        self.store_name = store_name
        self.amount = amount
        self.products = []

    def add_product(self, product):
        self.products.append(product)
