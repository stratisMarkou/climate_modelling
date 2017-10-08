import GPy
from netCDF4 import *
import os
import matplotlib.pyplot as plt
import numpy as np
import plotly
import copy

def flattenTrueSet(trueSet):
    return trueSet.reshape(trueSet.shape[0], -1)

def formatData(trueSet, batchSize, dayStep, pointIndex):
    X_train = []
    X_test = []
    y_train = []
    y_test = []
    startIndex = np.random.randint(low = 0, high = trueSet.shape[0] - batchSize*dayStep)
    
    for t in range(startIndex, startIndex+batchSize*dayStep):
        if (t-startIndex)%dayStep == 0:
            y_train.append(trueSet[t][pointIndex])
            X_train.append(t)
        else:
            y_test.append(trueSet[t][pointIndex])
            X_test.append(t)

    X_train = np.array([X_train]).T
    X_test = np.array([X_test]).T
    y_train = np.array([y_train]).T
    y_test = np.array([y_test]).T
    
    
    return X_train, X_test, y_train, y_test

np.random.seed(0)
os.chdir("/Users/Stratis/Documents/Climate Modelling/joint_data")

rootGroup = Dataset('cmip5-amip-tas_erai-T2.nc', 'r', format = "NETCDF4")
trueSet = np.array(rootGroup.variables["T2"])
trueSet = flattenTrueSet(trueSet)
trueSet -= trueSet.mean()

#set day increment (dayStep-1 days jumped)
dayStep = 5
#and range of days
timeRange = 1000

#get normalized training and test data
X_train, X_test, y_train, y_test = formatData(trueSet, timeRange//dayStep, dayStep, 25)
X_train = X_train/timeRange
X_test = X_test/timeRange
normFactor = y_train.var()**0.5
y_train = y_train/normFactor
y_test = y_test/normFactor

#create kernel and model, then optimize
ker_per = GPy.kern.PeriodicExponential(input_dim = 1, period = 1)
m = GPy.models.GPRegression(X_train, y_train, ker_per, noise_var = 0.5)
m.optimize()
print(m)
print((normFactor*(m.predict(X_test) - y_test)).var()**0.5)

#plot GP plus unseen data
m.plot()
plt.scatter(X_test, y_test)
plt.show()
