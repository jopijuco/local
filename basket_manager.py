class Basket_Manager():
    def __init__(self):
        self.basket = list()
    
    def get_list(self):
        return self.basket
    
    def add(self, product):
        self.basket.append(product)
    
    def remove(self, product):
        self.basket.remove(product)
    
    def get_name(string):
        name = string[string.find("name:"):]
        value = name[:name.find(",")]
        return value
    
    def total(self, field, products):
        total = 0
        for result in products:
            for dict in result:
                total += float(dict["price"])
        return total
    
    def empty_list(self):
        del self.basket[:]
