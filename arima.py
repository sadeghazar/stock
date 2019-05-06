from pandas import read_csv
from matplotlib import pyplot
from sklearn.metrics import mean_squared_error
from statsmodels.tsa.arima_model import ARIMA
import StockHistory
import pandas as pd
import numpy as np

# get data
def GetData():
    return StockHistory.get_namad_history_by_name('فخوز', from_cache=True)["ClosePrice"]


# Function that calls ARIMA model to fit and forecast the data
def StartARIMAForecasting(Actual, P, D, Q):
    model = ARIMA(Actual, order=(P, D, Q))
    model_fit = model.fit(disp=0)
    prediction = model_fit.forecast()[0]
    return prediction


# Get exchange rates
ActualData = GetData()
# Size of exchange rates
NumberOfElements = len(ActualData)

# Use 70% of data as training, rest 30% to Test model
TrainingSize = int(NumberOfElements * 0.7)
TrainingData = ActualData[0:TrainingSize]
TestData = ActualData[TrainingSize:NumberOfElements]

# new arrays to store actual and predictions
Actual = [x for x in TrainingData]
Predictions = list()

# in a for loop, predict values using ARIMA model
for timepoint in range(len(TestData)):
    ActualValue = TestData[timepoint]
    d = TestData.index[timepoint]
    # forcast value
    Prediction = np.float64(StartARIMAForecasting(Actual, 3, 1, 0)[0]).item()
    print('Actual=%f, Predicted=%f' % (ActualValue, Prediction))
    # add it in the list
    Predictions.append({"Date": d, "P": Prediction})
    Actual.append(ActualValue)

# Print MSE to see how good the model is
# Error = mean_squared_error(TestData, Predictions)
# print('Test Mean Squared Error (smaller the better fit): %.3f' % Error)
# plot
Predictions = pd.DataFrame(Predictions).set_index("Date")
pyplot.plot(TestData)
pyplot.plot(Predictions, color='red')
pyplot.show()
pass
