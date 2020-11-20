class Business:
    def __init__(self, id, name, description, phone, mobile, fiscal_number):
        self.id = id
        self.name = name
        self.description = description
        self.phone = phone
        self.mobile = mobile
        self.fiscal_number = fiscal_number
        self.stores = []

    def add_store(self, store):
        self.stores.append(store)
