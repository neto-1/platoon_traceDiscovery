from gurobipy import *






m2 = Model("pi2")
m2.ModelSense = -1
m2.setParam("OutputFlag", False)


x1 = m2.addVar(lb=0, obj= -27.0, vtype=GRB.CONTINUOUS, name="x1")
x2 = m2.addVar(lb=0, obj= -27.0, vtype=GRB.CONTINUOUS, name= "x2")

y1 = m2.addVar(lb=0, obj= -3.0, vtype=GRB.CONTINUOUS, name="y1")
y2 = m2.addVar(lb=0, obj= -1.0, vtype=GRB.CONTINUOUS, name= "y2")
y3 = m2.addVar(lb=0, obj= -1.0, vtype=GRB.CONTINUOUS, name="y3")
y4 = m2.addVar(lb=0, obj= -1.0, vtype=GRB.CONTINUOUS, name= "y4")
y5 = m2.addVar(lb=0, obj= -1.0, vtype=GRB.CONTINUOUS, name="y5")
y6 = m2.addVar(lb=0, obj= -1.0, vtype=GRB.CONTINUOUS, name= "y6")
y7 = m2.addVar(lb=0, obj= -3.0, vtype=GRB.CONTINUOUS, name="y7")

y8 = m2.addVar(lb=0, obj= -3.0, vtype=GRB.CONTINUOUS, name="y8")
y9 = m2.addVar(lb=0, obj= -1.0, vtype=GRB.CONTINUOUS, name= "y9")
y10 = m2.addVar(lb=0, obj= -1.0, vtype=GRB.CONTINUOUS, name="y10")
y11 = m2.addVar(lb=0, obj= -1.0, vtype=GRB.CONTINUOUS, name= "y11")
y12 = m2.addVar(lb=0, obj= -1.0, vtype=GRB.CONTINUOUS, name="y12")
y13 = m2.addVar(lb=0, obj= -1.0, vtype=GRB.CONTINUOUS, name= "y13")
y14 = m2.addVar(lb=0, obj= -3.0, vtype=GRB.CONTINUOUS, name="y14")

m2.update()


c1 = m2.addConstr(-x1 <= -1, "c1")
c2 = m2.addConstr(-x2 <= -1, "c2")

c3 = m2.addConstr(x1- y1 <= 0, "c3")

c4 = m2.addConstr(-y2 <= 0, "c4")
c5 = m2.addConstr(-y3<= 0, "c5")
c6 = m2.addConstr(-y4<= 0, "c6")
c7 = m2.addConstr(-y5<= 0, "c7")
c8 = m2.addConstr(-y6<= 0, "c8")
#c9 = m2.addConstr(-y7<= 0, "c9")
c9 = m2.addConstr(x2-y7<= 0, "c9")

c10 = m2.addConstr(-y8 <= 0, "c10")
c11 = m2.addConstr(-y9 <= 0, "c11")
c12 = m2.addConstr(-y10<= 0, "c12")
c13 = m2.addConstr(-y11<= 0, "c13")
c14 = m2.addConstr(-y12<= 0, "c14")
c15 = m2.addConstr(-y13<= 0, "c15")
c16 = m2.addConstr(-y14<= 0, "c16")

print(m2.obj)
c17 = m2.addConstr(- y1 <= 0, "c17")
#c18 = m2.addConstr(-y2 <= 0, "c18")
# c19 = m2.addConstr(-y3<= 0, "c19")
# c20 = m2.addConstr(-y4<= 0, "c20")
# c21 = m2.addConstr(-y5<= 0, "c21")
# c22 = m2.addConstr(-y11<= 0, "c22")
# c23 = m2.addConstr(-y7<= 0, "c23")

# c24 = m2.addConstr(-y1 <= 0, "c24")
# c25 = m2.addConstr(-y2 <= 0, "c25")
# c26 = m2.addConstr(-y3<= 0, "c26")
# c27 = m2.addConstr(-y4<= 0, "c27")
# c28 = m2.addConstr(-y5<= 0, "c28")
# c29 = m2.addConstr(-y6<= 0, "c29")
c30 = m2.addConstr(x2 -y7<= 0, "c30")



#c9 = m2.addConstr(x2 - y7<= 0, "c9")

m2.optimize()

print "x1", x1.x, "rc", x1.rc
print "x2", x2.x, "rc", x2.rc


print "x1 pi", c1.pi
print "x2 pi", c2.pi
print "y1 pi", c3.pi
print "y2 pi", c4.pi
print "y3 pi", c5.pi
print "y4 pi", c6.pi
print "y5 pi", c7.pi
print "y6 pi", c8.pi
print "y7 pi", c9.pi
print("---")

emptycons = []
for cons in m2.getConstrs():
    emptycons.append(cons.Pi)
    print(str(cons.ConstrName) + " " +str(cons.Pi))



print(emptycons)

