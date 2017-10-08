import GPy
from netCDF4 import *
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import plotly

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

def getTrainData(trueSet, days, blind_x, blind_y):
    input_t = []
    output_t = []

    for d in days:
        for i in range(trueSet.shape[1]):
            for j in range(trueSet.shape[2]):
                    if not(i in blind_y) or not(j in blind_x):
                        input_t.append([d, i, j])
                        output_t.append(trueSet[d, i, j])
                    
    input_t = np.array(input_t)
    output_t = np.array([output_t]).T
    
    return input_t, output_t

def getTestData(trueSet, days, blind_x, blind_y):
    input_t = []
    output_t = []

    for d in days:
        for i in range(trueSet.shape[1]):
            for j in range(trueSet.shape[2]):
                    if (i in blind_y) and (j in blind_x):
                        input_t.append([d, i, j])
                        output_t.append(trueSet[d, i, j])
                    
    input_t = np.array(input_t)
    output_t = np.array([output_t]).T
    
    return input_t, output_t

def getDataPreprocessed(file_location, filename):
    
    os.chdir(file_location)
    rootGroup = Dataset(filename, 'r', format = "NETCDF4")
    
    trueSet = np.array(rootGroup.variables["tas"])
    mean = trueSet[:, :, :].mean()
    trueSet = trueSet[:, :, :] - mean
    stddev = trueSet.var()**0.5
    trueSet = trueSet/stddev

    return trueSet, stddev

#get normalized data (set your own directory and filename)
trueSet, stddev = getDataPreprocessed(,)

np.random.seed(0)

#set day selection indices
days = np.arange(5)

#set unseen points of 19 by 13 grid
blind_x =  np.arange(0, 19, 3)
blind_y = np.arange(0, 13, 3)

#select training data (full data minus blind points on selected days)
train_x, train_y = getTrainData(trueSet, days, blind_x, blind_y)

#set up 3d rbf kernel and optimize
ker_rbf = GPy.kern.RBF(input_dim = 3, lengthscale = 1)
m = GPy.models.GPRegression(train_x, train_y, ker_rbf)
m.optimize()
print(m)

#select test data (blind points on selected days) and predict
test_x, test_y = getTestData(trueSet, days, blind_x, blind_y)
prediction = m.predict(test_x)[0]

#get error std deviation for test data
errors = (test_y-prediction).flatten().tolist()
print(stddev*np.array(errors).var()**0.5)

