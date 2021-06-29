class Contract:
    def __init__(self, contractID=0, name=None, email=None, phone=None, sent=False, lastDateSent=None):
        self.contractID = contractID
        self.name = name
        self.email = email
        self.phone = phone
        self.sent = sent
        self.lastDateSent = lastDateSent
