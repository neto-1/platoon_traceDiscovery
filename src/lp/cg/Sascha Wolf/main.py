from gurobipy import *

#roll_width = 560
#
## demand, length
#demand = [
#    (22, 138),
#    (25, 152),
#    (12, 156),
#    (14, 171),
#    (18, 182),
#    (18, 188),
#    (20, 193#),
#    (10, 200),
#    (12, 205),
#    (14, 210),
#    (16, 214),
#    (18, 215),
#    (20, 220)
#]

roll_width = 218
demand = [
    (44, 81),
    (3, 70),
    (48, 68)
]

initial = Model('initial')

initial_partitions = []
for key in range(len(demand)):
    initial_partitions.append(initial.addVar(vtype=GRB.CONTINUOUS, name='x' + str(key)))

initial.setObjective(sum(initial_partitions), GRB.MINIMIZE)

for key, partition in enumerate(initial_partitions):
    initial.addConstr(int(roll_width / demand[key][1]) * partition >= demand[key][0])

initial.optimize()

print([constraint.Pi for constraint in initial.getConstrs()])
