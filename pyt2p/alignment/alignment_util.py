try:
    '''numpy's log provides more float precision'''
    from numpy import log, exp, isinf
except ImportError:
    from math import log, exp, isinf

def logAdd(logX, logY):
    # make logX the max of the wo
    if logY > logX:
        logX, logY = logY, logX

    negDiff = logY - logX
    #print negDiff
    if negDiff < -20:
        return logX

    return (logX + log(1.0 + exp(negDiff)))

def logSum(log_sequence):
    return reduce(lambda x,y: logAdd(x,y), log_sequence)
