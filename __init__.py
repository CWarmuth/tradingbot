import matplotlib.pyplot as plt
import pricefinder

# calculates all the values we need
dates, prices, rolling_price_avg, rolling_derivative_avg, rolling_second_derivative = pricefinder.findprices_derivative("180")

# sets up the graphs
fig, (axs1, axs2) = plt.subplots(1, 2, figsize=(12, 6))

# creates the left and right graphs
axs1.plot(dates, prices, label="prices")
axs1.plot(dates, rolling_price_avg, label="rolling average")

axs2.plot(dates, rolling_derivative_avg, label="rolling derivative average")
axs2.plot(dates, rolling_second_derivative, label="rolling second derivative average")

plt.xlabel('x axis')

plt.ylabel('y axis')

axs1.set_title("bitcoin prices")
axs1.legend()

axs2.set_title("derivatives")
axs2.legend()
# rotates ticklabels for axs1 and axs2
plt.setp(axs1.xaxis.get_majorticklabels(), rotation=25)
plt.setp(axs2.xaxis.get_majorticklabels(), rotation=25)

# threshold for which bitcoin should be bought or sold
threshold = 0.4

# how much money you start with
balance = 5000
# how many bitcoins you start with
bitcoins = 0.1
starting_budget = balance + prices[0] * bitcoins
# used to prevent buying and selling close together
lastbuysell = -1
amountlostonfees = 0
# calculates your total balance at the beginning, using the price of bitcoin at the start time.
print("starting balance: " + str(starting_budget))
for i in range(10, len(rolling_derivative_avg)):
    # should be between -1 and 1
    buysell = pricefinder.buysell(rolling_derivative_avg[0:i], rolling_second_derivative[0:i])
    # if the value exceeds the threshold, then we need to buy btc. Also checks that we haven't too recently bought or
    # sold
    if buysell > threshold and i - lastbuysell > 20:
        # buys bitcoins based on how high the buysell value is.
        bitcoins_bought_attempt = balance * buysell / prices[i]
        bitcoins_bought = max(0.0, min(bitcoins_bought_attempt, bitcoins_bought_attempt - balance / prices[i]))
        fee = bitcoins_bought * prices[i] * 0.002
        balance -= fee
        amountlostonfees += fee
        # Adds bought bitcoins to the total and subtracts from the cash balance
        bitcoins += bitcoins_bought
        balance -= bitcoins_bought * prices[i]
        # Addes the label to the graph
        axs1.annotate("buy at " + str(prices[i]), (dates[i], prices[i]))
        # Resets the lastbuysell value
        lastbuysell = i
    elif buysell < -threshold and i - lastbuysell > 20:
        # sells bitcoins based on the value of buysell
        bitcoins_sold_attempt = bitcoins * -buysell
        bitcoins_sold = max(bitcoins_sold_attempt, bitcoins_sold_attempt - bitcoins)
        fee = bitcoins_sold * prices[i] * 0.002
        balance -= fee
        amountlostonfees += fee
        # Adds money to the cash balance and removes bitcoins from the total
        balance += bitcoins_sold * prices[i]
        bitcoins -= bitcoins_sold
        # Adds label to graph
        axs1.annotate("sell at " + str(prices[i]), (dates[i], prices[i]))
        # Resets lastbuysell value
        lastbuysell = i

# Calculates the total balance based on prices at the end
final_balance = balance + prices[-1] * bitcoins
print("final balance: " + str(final_balance))
print("Lost " + str(amountlostonfees) + " on fees")
print("Made " + str(final_balance - starting_budget) + " over " + str(dates[-1] - dates[0]))
plt.show()
quit()
