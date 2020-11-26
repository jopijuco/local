class Order:
    def __init__(self, id, date, amount, status, store_id):
        self.id = id
        self.date = date
        self.amount = amount
        self.status = status
        self.store_id = store_id
        self.products = []

    #def add_product(self, product):
        #self.products.append(product)
