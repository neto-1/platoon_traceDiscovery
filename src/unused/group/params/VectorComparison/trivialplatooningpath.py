import numpy
import numpy as np
from scipy.optimize import minimize
from gurobipy import *
#import networkx as nx
import string


#startpunkt von veh1#
p12= np.array([2,3])
#startpunkt von veh2#
p13= np.array([3,12])
#endpunkt von veh1#
p22= np.array([7,4])
#endpunkt von veh2#
p23= np.array([9,2])


###Distannces berechnen###
#StreckevonVeh1(RoadDistance)#
rdVeh2= ((p22[0]-p12[0])**2+(p22[1]-p12[1])**2)**0.5
#StreckevonVeh2#
rdVeh1= ((p23[0]-p13[0])**2+(p23[1]-p13[1])**2)**0.5
#Streckevonp12zup13#
rdStarts= ((p13[0]-p12[0])**2+(p13[1]-p12[1])**2)**0.5
#Streckevonp22zup23#
rdEnds= ((p23[0]-p22[0])**2+(p23[1]-p22[1])**2)**0.5
#SinglePath#
SP=rdVeh1+rdVeh2
print(rdVeh1)
print(rdVeh2)
if rdVeh1<rdVeh2:
    rdVeh1 = rdVeh2
    rdVeh2 = SP - rdVeh1

TPSP= rdVeh2+rdStarts+rdEnds+0.9*rdVeh2

TPPvalue= TPSP/SP


print(TPPvalue)

