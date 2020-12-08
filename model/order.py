class Order:
    def __init__(self, id, date, amount, status, status_id, store, customer):
        self.id = id
        self.date = date
        self.amount = amount
        self.status = status
        self.status_id = status_id
        self.store = store
        self.customer = customer
        self.products = []

    def add_product(self, product):
        self.products.append(product)

class Product_ordered:
    def __init__(self, name, quantity, final_price):
        self.name = name
        self.quantity = quantity
        self.final_price = final_price
