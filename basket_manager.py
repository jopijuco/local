class Basket_Manager():
    def __init__(self):
        self.basket = {}
    
    def get_list(self):
        return self.basket
    
    def add(self, product_id, quantity):
        self.basket[product_id] = quantity
    
    def remove(self, product_id):
        del self.basket.remove[product_id]
    
    # def get_name(string):
    #     name = string[string.find("name:"):]
    #     value = name[:name.find(",")]
    #     return value
    
    def total(self, field, products):
        total = 0
        for result in products:
            for dict in result:
                total += float(dict[field])
        return total
    
    def empty_basket(self):
        del self.basket[:]
