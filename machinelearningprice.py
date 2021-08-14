import requests
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
import tensorflow as tf
import pricefinder as pf

from tensorflow.keras import layers
from tensorflow.keras.layers.experimental import preprocessing

BINANCE_API_KEY = "nmN2RxNWh8yJXqEKf21IP84bV7zKVZHBfdu8BUjjzD7KcjnJoMEM1ri1vgP8ZO8Q"
BINANCE_API_BASE = "https://api.binance.us"

TRAIN_END = 10
LIMIT = 500


def setup(interval, **kwargs):
    if kwargs.get("endTime") is not None:
        request = BINANCE_API_BASE + "/api/v3/klines?symbol=BTCUSDT&interval=" + interval + "&endTime="\
                  + str(kwargs.get("endTime")) + "&limit=" + str(LIMIT)
    elif kwargs.get("startTime") is not None:
        request = BINANCE_API_BASE + "/api/v3/klines?symbol=BTCUSDT&interval=" + interval + "&startTime=" \
                  + str(kwargs.get("startTime")) + "&limit=" + str(LIMIT)
    else:
        request = BINANCE_API_BASE + "/api/v3/klines?symbol=BTCUSDT&interval=" + interval + "&limit=" + str(LIMIT)
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
    #time.sleep(1)
    return response_json


def setup_graph(data):
    utctimes = data[:, 0]
    utctimes = np.array(list(map(int, utctimes))) / 1000
    date_convert = np.vectorize(datetime.fromtimestamp)
    dates = date_convert(utctimes)

    pricesstring = data[:, 4]
    prices = np.array(list(map(float, pricesstring)))
    fig, (axs1, axs2) = plt.subplots(1, 2, figsize=(12, 6))
    axs1.plot(dates, prices, label="prices")
    return fig, (axs1, axs2)


def setup_datapoint(data, datapoint_index):
    newdata = np.empty((LIMIT - TRAIN_END) * 1)

    open_price = np.array(list(map(float, data[0:LIMIT - TRAIN_END, 1])))  # Open price
    close_price = np.array(list(map(float, data[0:LIMIT - TRAIN_END, 4])))  # Close price
    volume = np.array(list(map(float, data[0:LIMIT - TRAIN_END, 5])))  # Volume
    num_trades = np.array(list(map(float, data[0:LIMIT - TRAIN_END, 8])))  # Number of trades

    # The training features are drawn from the first data point to the
    # last data point minus the TRAIN_END value.
    newdata[0:LIMIT - TRAIN_END] = pf.rollingaverage(open_price, 20)
    #newdata[LIMIT - TRAIN_END:(LIMIT - TRAIN_END) * 2] = pf.rollingaverage(close_price, 20)
    #newdata[(LIMIT - TRAIN_END) * 2:(LIMIT - TRAIN_END) * 3] = volume
    #newdata[(LIMIT - TRAIN_END) * 3:(LIMIT - TRAIN_END) * 4] = num_trades
    # The y value is then halfway from the end of the training features to the end of the data. Should be changed.
    ydata = data[LIMIT - TRAIN_END: LIMIT - TRAIN_END + datapoint_index, 1]
    return newdata, ydata


def setup_multiple_datapoints(datapoints, interval, datapoint_index):
    xvals = np.empty((datapoints, (LIMIT - TRAIN_END) * 1))
    yvals = np.empty(datapoints)
    for i in range(datapoints):
        setback = np.random.randint(0, 31556926)
        end = int(datetime.timestamp(datetime.now()))
        end = end - setback
        end *= 1000
        data = setup(interval, endTime=end)
        xdatapoint, ydatapoint = setup_datapoint(data, datapoint_index)
        xvals[i] = xdatapoint
        yvals[i] = ydatapoint
    return xvals, yvals


def setup_ml(X_train, Y_train):
    normalizer = preprocessing.Normalization()
    normalizer.adapt(X_train)

    model = tf.keras.Sequential([
        normalizer,
        layers.Dense(units=1)
    ])
    model.compile(
        optimizer=tf.optimizers.Adam(learning_rate=0.1),
        loss='mean_absolute_error'
    )
    history = model.fit(
        X_train, Y_train,
        epochs=1000,
        verbose=0,
        validation_split=0.2
    )
    test = X_train[:10]
    prediction = model.predict(test)
    print("Predicted: ", prediction, "Actual: ", Y_train[:10])
    return


if __name__ == "__main__":
    data_json = setup("1h")
    train_x, train_y = setup_multiple_datapoints(100, "1h", 1)
    setup_graph(data_json)
    setup_ml(train_x, train_y)
    plt.show()
