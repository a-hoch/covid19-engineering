import pandas as pd
import numpy as np
import datetime
from statsmodels.tsa.arima_model import ARIMA
import math
import boto3
import botocore
import pickle
import tarfile
import os

from sagemaker_training import environment

# Reading Env configuration from 
env = environment.Environment()
model_dir = env.model_dir
prediction_target = env.hyperparameters['prediction_target']


def prepareData():
    startDate = datetime.date(2020, 1, 22)
    urlFormat = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/5bc15023f39b2a92844928e7f0d66b2aca5ee304/csse_covid_19_data/csse_covid_19_daily_reports/{}.csv"
    endDate = datetime.date(2020, 3, 21)
    rawDataArray = []

    while(startDate != endDate):
        dateString = startDate.strftime("%m-%d-%Y")
        url = urlFormat.format(dateString)
        print("url:{}\n".format(url))
        df = pd.read_csv(url, error_bad_lines=False)
        rawDataArray.append(df)
        startDate += datetime.timedelta(days=1)


    rawDf = pd.concat(rawDataArray, sort=True)

    filteredDf = rawDf[rawDf["Country/Region"] == "US"]
    filteredDf['Date']= pd.to_datetime(filteredDf['Last Update'])
    filteredDf.drop("Last Update", axis=1, inplace=True)
    filteredDf = filteredDf[["Date","Confirmed","Deaths","Recovered"]]
    dateCol = filteredDf.apply(lambda row: row["Date"].date(), axis=1)
    filteredDf["Date"] = dateCol

    aggDf = filteredDf.groupby('Date').agg({'Confirmed': ['sum','mean', 'min', 'max'], 
                                           'Deaths': ['sum','mean', 'min', 'max'],
                                            'Recovered': ['sum','mean', 'min', 'max']
                                           }).reset_index()
    columnMapping = ["Date",
                     "Confirmed",
                     "Confirmed_mean",
                     "Confirmed_min",
                     "Confirmed_max",
                     "Deaths",
                     "Deaths_mean",
                     "Deaths_min",
                     "Deaths_max",
                     "Recovered",
                     "Recovered_mean",
                     "Recovered_min",
                     "Recovered_max"
                    ]

    aggDf.columns = columnMapping

    return aggDf.sort_values("Date")

def forecast_accuracy(forecast, actual):
    mape = np.mean(np.abs(forecast - actual)/np.abs(actual))  # MAPE
    me = np.mean(forecast - actual)             # ME
    mae = np.mean(np.abs(forecast - actual))    # MAE
    mpe = np.mean((forecast - actual)/actual)   # MPE
    rmse = np.mean((forecast - actual)**2)**.5  # RMSE
    corr = np.corrcoef(forecast, actual)[0,1]   # corr
    mins = np.amin(np.hstack([forecast[:,None], 
                              actual[:,None]]), axis=1)
    maxs = np.amax(np.hstack([forecast[:,None], 
                              actual[:,None]]), axis=1)
    minmax = 1 - np.mean(mins/maxs)             # minmax
    return({'mape':mape, 'me':me, 'mae': mae, 
            'mpe': mpe, 'rmse':rmse,
            'corr':corr, 'minmax':minmax})

def CreateAndEvaluateModel(target, df, splitPct = 0.8): 
    # Find Index to Split on
    count = sortedDf.Date.count()
    index = math.floor(count * splitPct)
    
    # Create Training and Test 
    train = df[target][:index]
    test = df[target][index:]

    # Build Model
    # model = ARIMA(train, order=(3,2,1))  
    model = ARIMA(train, order=(1, 1, 1))  
    fitted = model.fit()  

    # Forecast
    fc, se, conf = fitted.forecast(test.count(), alpha=0.05)  # 95% conf
    print("ForecastAccuracy: {}\n\n\n".format(forecast_accuracy(fc, test.values)))
    return  model

def serializeModel(model, target):
    with open(os.path.join(model_dir, "model_{}.pkl".format(target)), 'wb') as pkl:
        pickle.dump(model, pkl)

##########################################################
# Creating Model
##########################################################

print('Creating Model For {}'.format(prediction_target))

sortedDf = prepareData()
model = CreateAndEvaluateModel(prediction_target, sortedDf)
serializeModel(model, prediction_target)