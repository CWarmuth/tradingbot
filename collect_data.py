from datetime import datetime

import requests
import numpy as np
import pandas as pd

BINANCE_API_KEY = "nmN2RxNWh8yJXqEKf21IP84bV7zKVZHBfdu8BUjjzD7KcjnJoMEM1ri1vgP8ZO8Q"
BINANCE_API_BASE = "https://api.binance.us"

LIMIT = 500
num_data_sets = 50

def pull_request(interval, endTime):
    request = BINANCE_API_BASE + "/api/v3/klines?symbol=BTCUSDT&interval=" + interval + "&endTime="\
              + str(endTime) + "&limit=" + str(LIMIT)

    response = requests.get(request)
    response_json = np.asarray(response.json())
    status_code = response.status_code

    if status_code != 200:
        print("failed with status code: ", status_code)
        if status_code == 418:
            print("retry after ", response_json["Retry-After"])
        if status_code == 418:
            print("retry after ", response_json["Retry-After"])
        quit(-1)
    return response_json

def load_set():
    starting_end_time = 1569888000 + 449100
    prices = list()
    dates = list()

    for i in range(num_data_sets):
        json = pull_request("15m", starting_end_time * 1000)
        starting_end_time += 449100

        pricesstring = json[:, 4]
        new_prices = list(map(float, pricesstring))

        utctimes = json[:, 0]
        utctimes = list(map(int, utctimes))

        prices.extend(new_prices)
        dates.extend(utctimes)

    csv = np.column_stack((dates, prices))
    DF = pd.DataFrame(csv)
    DF.to_csv("data.csv")

if __name__ == "__main__":
    load_set()
