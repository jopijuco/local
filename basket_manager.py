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