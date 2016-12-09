class Customer:
    def __init__(self, id, name, pointBalance, activityStatus=True, receipts=None, reservations=None):
        self.customer_id = id
        self.customer_name = name
        self.customer_balance = pointBalance
        self.is_active = activityStatus
        self.customer_receipts = receipts
        self.customer_reservations = reservations

