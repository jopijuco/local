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
    
    def total(self, full_basket):
        total = 0
        for b in full_basket.baskets:
            print("------->"+str(b.amount))
            total += float(b.amount)
        return total
    
    def get_store_list(self):
        store_list = []
        for key in self.basket:
            store_list.append(key[1])
        #remove doublon from store_list
        return list(set(store_list))
    
    def empty_basket(self):
        del self.basket[:]
