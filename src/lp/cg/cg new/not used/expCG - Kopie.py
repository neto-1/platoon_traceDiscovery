from gurobipy import *
from mainCG import column_generation_platooning
import json


# ========== needed input:
# saving factor
# set ID OR size and distribution
# with OR without grouping first

# ==================== INITIAL PARAMETERS ====================
idSet = sys.argv[2]
savings = float(sys.argv[3])

# ========== initial path:
# first is for the shortest path (include shortestPath = 1)
# second is for the "best pair" path (include "best Pair" = 1)
# third is for creating all relevant paths through the vehicle hull intersections
# forth is indicating to delete all paths after iteration (=1) or not (=0)
init_shortest_path = 1
init_best_pair = 1
init_best_pair_callback = 0
delete_path = 1

# ===== This variable is only for the output! it doesnt change the process of column generation ######
# first is for output of the actual paths and shortest path calculations
# second is to show the optimal solution and the shortest path solution of the normal LP for platooning
# third is for output the actual solution of the iteration of CG
# forth is for the set id and the ids of the considered vehicles
# fifth is the output of the results of the set of vehicles
output_showing = 1

# ==================== COLUMN GENERATION FUNCTION ====================
(output_data) = column_generation_platooning(savings, idSet, init_shortest_path, init_best_pair,
                                             init_best_pair_callback, delete_path, output_showing)

# return value
print(json.dumps(output_data))
