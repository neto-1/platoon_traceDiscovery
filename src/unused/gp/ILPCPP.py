from gurobipy import *
from DB import DB


model = Model("Grouping")
model.setParam("OutputFlag", True)
model.ModelSense = GRB.MAXIMIZE

i_m = DB.get_incentive_matrix("")
m = i_m.get_matrix_copy_with_penalty()

x = {}
for i in range(len(m)):
    for j in range(i + 1, len(m)):
        if i != j:
            x[i, j] = model.addVar(vtype=GRB.BINARY, lb=0, obj=m[i][j])
            x[j, i] = x[i, j]
model.update()
# print x
for i in range(len(m)):
    for j in range(len(m)):
        for r in range(len(m)):
            if i != j and i != r and j != r:
                model.addConstr(x[i, j] + x[i, r] - x[j, r] <= 1)

model.optimize()

print model.ObjVal
