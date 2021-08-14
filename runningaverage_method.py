import numpy as np
import matplotlib.pyplot as plt
import machinelearningprice as mlp
import pricefinder as pf
import time
from wallet_class import Wallet
from datetime import datetime

threshold = 0.04
interval = 20
moving_interval = 150
amount_to_buy_sell = 0.2

def testbuysell(**kwargs):
    fig, axs = plt.subplots(1, 1, figsize=(6, 6))

    json = mlp.setup("15m", endTime=int(kwargs.get("endTime") * 1000))
    wallet = kwargs.get("wallet")
    sell_predictions = list()
    buy_predictions = list()
    thresholds = list()

    time.sleep(1)
    pricesstring = json[:, 4]
    prices = np.array(list(map(float, pricesstring)))
    rollingprices = pf.rollingaverage(prices, moving_interval)

    utctimes = json[:, 0]
    utctimes = np.array(list(map(int, utctimes))) / 1000
    date_convert = np.vectorize(datetime.fromtimestamp)
    dates = date_convert(utctimes)

    last = 0
    starting_budget = wallet.dollars + prices[0] * wallet.bitcoins
    amountlostonfees = 0

    for i in range(0, len(rollingprices)):
        last += 1
        current_btc_price = prices[i]
        buy_predictions.append(rollingprices[i] - prices[i])
        sell_predictions.append(prices[i] - rollingprices[i])
        thresholds.append(rollingprices[i] * threshold)
        if rollingprices[i] - prices[i] > rollingprices[i] * threshold and last > interval:
            # buys bitcoins based on how high the buysell value is.
            # withdraw enough money to make the purchase
            available_cash = wallet.withdraw_money(amount_to_buy_sell * prices[i])
            bitcoins_bought = available_cash / current_btc_price
            fee = bitcoins_bought * 0.002
            bitcoins_bought -= fee
            # Adds bought bitcoins to the total and subtracts from the cash balance
            wallet.deposit_btc(bitcoins_bought)
            amountlostonfees += fee * current_btc_price
            # Resets the lastbuysell value
            last = 0
            # Addes the label to the graph
            if bitcoins_bought > 0.0001:
                print("Bought ", bitcoins_bought, "at", prices[i], str(dates[i]), "(moving average at:", rollingprices[i], ")")
                axs.annotate("buy at " + str(prices[i]), (dates[i], prices[i]))
        elif prices[i] - rollingprices[i] > rollingprices[i] * threshold and last > interval:
            # sells bitcoins based on the value of buysell
            available_btc = wallet.withdraw_btc(amount_to_buy_sell)
            fee = available_btc * 0.002
            available_btc -= fee
            amountlostonfees += fee * current_btc_price
            # Adds money to the cash balance and removes bitcoins from the total
            wallet.deposit_money(available_btc * current_btc_price)
            # Adds label to graph
            # Resets lastbuysell value
            last = 0
            if available_btc > 0.0001:
                print("Sold ", available_btc, "at", current_btc_price, str(dates[i]), "(moving average at:", rollingprices[i], ")")
                axs.annotate("sell at " + str(current_btc_price), (dates[i], current_btc_price))

    final_balance = wallet.dollars + prices[-1] * wallet.bitcoins
    print("Made " + str(final_balance - starting_budget) + " over " + str(dates[-1] - dates[0]))

    axs.plot(dates, prices, label="prices")
    axs.plot(dates, rollingprices, label="rolling average")

    ax2 = axs.twinx()
    ax2.plot(dates, sell_predictions, label="sell predictions", color='red')
    ax2.plot(dates,buy_predictions, label="buy predictions", color='green')
    ax2.plot(dates, thresholds, label="thresholds", color='purple')
    ax2.legend()

    axs.legend()
    plt.show()
    return wallet, utctimes[-1]


if __name__ == "__main__":
    tests = 50
    endtime = 1569888000 + 449100
    startingdollars = 7000
    startingbtc = 1
    wallet = Wallet(startingbtc, startingdollars)
    for _ in range(tests):
        wallet, endtime = testbuysell(endTime=endtime + 449100, wallet=wallet)
        print(wallet.tostring())
    print("Turned $", startingdollars, " and ", startingbtc, " btc into ")
    print(wallet.tostring())
    quit()