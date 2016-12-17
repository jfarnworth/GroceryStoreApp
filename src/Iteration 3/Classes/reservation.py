class Reservation:
    def __init__(self, resID, custID, date, barcodes, quantities):
        self.reservation_id = resID
        self.customer_id = custID
        self.date = date
        self.barcodes = barcodes
        self.quantities = quantities