from netCDF4 import *
import numpy as np
import tensorflow as tf
import math

def trim(modelTemps):
    minTime = 10**10
    for model in modelTemps:
        if model.shape[0] < minTime:
            minTime = model.shape[0]
            
    for i in range(len(modelTemps)):
        modelTemps[i] = modelTemps[i][:minTime,:,:]
        
        
    return np.stack(modelTemps, axis = 0)

def getOptimizedWeights(trueSet, models, selectionArray, heldbackArray, learningParams, statusbar):

    learning_rate, max_steps, min_rate, min_diff, alpha = learningParams
    input_y = trueSet[selectionArray, :, :]
    input_x = models[:, selectionArray, :, :]
    heldback_y = trueSet[heldbackArray, :, :]
    heldback_x = models[:, heldbackArray, :, :]

    t_shape = input_y.shape
    h_shape = heldback_x.shape
    m_shape = input_x.shape
    y_t = tf.placeholder(tf.float32, [None, t_shape[1], t_shape[2]])
    x = tf.placeholder(tf.float32, [m_shape[0], None, m_shape[2], m_shape[3]])
    w = tf.Variable(tf.zeros([m_shape[0], m_shape[2], m_shape[3]]))
    y_m = tf.einsum('mxy,mtxy->txy', w, x)
    
    loss_reg = tf.reduce_sum((y_t - y_m) * (y_t - y_m)) + alpha*tf.reduce_sum(w*w)
    loss_real = tf.reduce_sum((y_t - y_m) * (y_t - y_m))
    step = learning_rate/(m_shape[0]*m_shape[1]*m_shape[2]*m_shape[3])

    train_step = tf.train.GradientDescentOptimizer(step).minimize(loss_reg)

    sess = tf.Session()
    sess.run(tf.initialize_all_variables())
    
    previous_loss = 10**50
    current_loss = 10**49

    errors = []
    heldback = []
    step = 0
    rate_sf = int(abs(math.log(min_rate, 10))+0.5)
    diff_sf = int(abs(math.log(min_diff, 10))+0.5)
    
    while checkQuitConditions(learningParams, step, previous_loss, current_loss):
        temp_loss = current_loss
        _, current_loss = sess.run([train_step, loss_real], feed_dict={x: input_x,
                                    y_t: input_y})
        current_loss = (current_loss/t_shape[0]/t_shape[1]/t_shape[2])**0.5
        previous_loss = temp_loss
        
        errors.append((sess.run(loss_real, feed_dict = {x: input_x, y_t: input_y})
                        /t_shape[0]/t_shape[1]/t_shape[2])**0.5)
        heldback.append((sess.run(loss_real, feed_dict = {x: heldback_x, y_t: heldback_y})
                        /h_shape[1]/h_shape[2]/h_shape[3])**0.5)

        step += 1
        statusbar.SetStatusText("Training...   " + "step: " + str(step) +
                                ", error [current: " + str(round(errors[-1], 4)) +
                                ", heldback: " + str(round(heldback[-1], 4)) +
                                ", rate of change: -" +
                                str(round((previous_loss - current_loss)/current_loss, rate_sf)) + 
                                ", change: -" + str(round(previous_loss - current_loss, diff_sf))
                                + "]")
            
        print(current_loss, heldback[-1])
        
    return w.eval(session = sess), errors, heldback

def checkQuitConditions(learningParams, step, previous_loss, current_loss):

    learning_rate, max_steps, min_rate, min_diff, alpha = learningParams
    
    if not(max_steps == None):
        if step > max_steps:
            return False
    
    if not(min_rate == None):
        if min_rate > (previous_loss - current_loss)/current_loss:
            return False

    if not(min_diff == None):
        if min_diff > (previous_loss - current_loss):
            return False
            
    return True

def evaluateBestModels(obsDataset, modelDatasets, selectionArray):

    gridShape = obsDataset.shape[1:]
    bestModelPatchwork = np.zeros(shape = gridShape) - 1

    true = obsDataset[selectionArray, :, :]
    models = modelDatasets[:, selectionArray, :, :]

    for i in range(gridShape[0]):
        for j in range(gridShape[1]):
            lowestError = float("inf")
            bestModel = -1
            for m in range(modelDatasets.shape[0]-1):
                currentError = ((true[:, i, j] - models[m, :, i, j])**2).mean()
                if currentError < lowestError:
                    lowestError = currentError
                    bestModel = m
                    
            bestModelPatchwork[i, j] = bestModel

    return bestModelPatchwork




    
