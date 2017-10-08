import numpy as np

def setSelectionArray():
    #Returns numpy ndarray of integers
    #Each entry represents the index of
    #a training datapoint

    #Your expression under this line.

    #Make sure something is returned!
    return

def setHeldbackArray():
    #Returns numpy ndarray of integers
    #Each entry represents the index of
    #a heldback datapoint

    #Your expression under this line.

    #Make sure something is returned!
    return

def setTrainingParameters():
    #Returns tuple of numbers:
    #(learning_rate, maximum_steps, min_rate, min_diff, alpha)
    #training stops if:
    #   max_steps > steps
    #   min_rate > rate of change of objective error
    #   min_diff > change of objective error
    
    #learning_rate: learning rate
    #(automatically scaled by dataset size)
    learning_rate = 1
    
    #max_steps: maximum number of learning steps
    #(if None, training stops through min_rate and/or min_diff)
    max_steps = 200
    
    #min_rate: minimum rate of change of objective error
    #(if None, training stops through maximum_steps and/or min_diff)
    min_rate = 10**-3

    #min_diff: minimum change of objective error
    #(if None, training stops through maximum_steps and/or min_diff)
    min_diff = 10**-3

    #alpha: regularization coefficient
    alpha = 0

    return (learning_rate, max_steps, min_rate, min_diff, alpha)
    
