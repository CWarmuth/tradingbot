class Wallet:

    def __init__(self, bitcoins=0, dollars=0):
        self.bitcoins = bitcoins
        self.dollars = dollars

    def deposit_money(self, amount):
        self.dollars += amount
        return amount

    def deposit_btc(self, amount):
        self.bitcoins += amount
        return amount

    def withdraw_money(self, amount):
        self.dollars -= min(amount, self.dollars)
        return min(amount, self.dollars)

    def withdraw_btc(self, amount):
        self.bitcoins -= min(amount, self.bitcoins)
        return min(amount, self.bitcoins)

    def balance(self):
        return self.dollars, self.bitcoins

    def tostring(self):
        return "Total dollars: " + str(self.dollars) + ", Total btc: " + str(self.bitcoins)