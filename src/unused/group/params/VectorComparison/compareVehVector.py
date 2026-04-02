import numpy
import numpy as np
from scipy.optimize import minimize
from gurobipy import *
import string


vec1= np.array ([1,2])
vec2= np.array ([7,8])

###Funktion von comparevehvector winkelberechnung zwischen zwei vektoren###
def compareVector(vec1,vec2):
    """compareVector"""
    #skalarprodukt#
    skalProd = np.dot(vec1, vec2)
    #betrag von x#
    vec1_betrag = np.sqrt((vec1 * vec1).sum())
    #betrag von y#
    vec2_betrag = np.sqrt((vec2 * vec2).sum())

    #berechnung des cos_angle#
    winkel = skalProd / (vec1_betrag * vec2_betrag)
    return winkel

#result#
res= compareVector(vec1,vec2)

print (res)



