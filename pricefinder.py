import requests
import datetime
import numpy

API_KEY = "XQT0C5LT0UEZDJOR8WKU"
API_KEY_PRIVATE = "llQhM0XrokZF5NtN6YSuFJZm1CyZbcX40sFx5BT8"
PRICE_ROLLING_AVERAGE_SIZE = 19
PRICE_DERIVATIVE_ROLLING_AVERAGE_SIZE = 18
PRICE_SECOND_DERIVATIVE_ROLLING_AVERAGE_SIZE = 7

# finds the linear rolling average of a list of values. moving_avg_size specifies the size of the moving average.
def rollingaverage(values, moving_avg_size):
    arg0 = [values[0]]
    for i in range(1, len(values)):
        numerator = 0
        denominator = 0
        startval = max(0, i - moving_avg_size)
        for j in range(startval, i + 1):
            numerator += values[j] * (j - startval)
            denominator += (j - startval)
        arg0.append(numerator / denominator)
    return arg0


# takes the derivatives of a list of values
def takederivative(values):
    derivative = []
    for i in range(1, len(values)):
        prev_val = values[i - 1]
        if i == 1:
            derivative.append(values[i] - prev_val)
        derivative.append(values[i] - prev_val)
    return derivative


# fetches the prices and finds the derivative of them
def findprices_derivative(time):
    response = requests.get("https://api.cryptowat.ch/markets/gemini/btcusd/ohlc?apikey=" + API_KEY)
    response_json = response.json()["result"][time]
    dates = list()
    prices = list()
    for i in response_json:
        dates.append(datetime.datetime.fromtimestamp(int(i[0])))
        prices.append(i[1])
    rpa = rollingaverage(prices, PRICE_ROLLING_AVERAGE_SIZE)
    price_derivative = takederivative(rpa)
    rda = rollingaverage(price_derivative, PRICE_DERIVATIVE_ROLLING_AVERAGE_SIZE)
    second_derivative = takederivative(price_derivative)
    r2da = rollingaverage(second_derivative, PRICE_SECOND_DERIVATIVE_ROLLING_AVERAGE_SIZE)
    return dates, prices, rpa, rda, r2da


# returns a number between -1 and 1 which reflects how much should be sold or bought, respectively
def buysell(derivatives, rolling_second_derivative):
    if derivatives[-1] == 0 or (derivatives[-2] > 0 > derivatives[-1]) or (derivatives[-2] < 0 < derivatives[-1]):
        return -numpy.arctan(rolling_second_derivative[-1]) / numpy.pi
    else:
        return 0
