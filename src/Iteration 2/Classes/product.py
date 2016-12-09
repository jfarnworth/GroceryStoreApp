class Product:
    def __init__(self, product_name, product_barcode, product_available, product_price, product_customer_price, weigh, product_provider):
        self.name = product_name
        self.barcode = product_barcode
        self.available = product_available
        self.price = product_price
        self.customer_price = product_customer_price
        self.weigh_b = weigh
        self.provider = product_provider
