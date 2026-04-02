library(yaml)
print("R: Convex Algorithm")
args = commandArgs(trailingOnly=TRUE)

vehicles = (as.numeric(args[1]))
groups = (as.numeric(args[2]))
ownPath = args[3]
testid = (as.numeric(args[4]))
vehtype = args[5]


postfix = "/group/convex/"

LimitValue = vehicles
kGroups = groups
completeSource = paste0(ownPath,postfix,"main.r")
ownPath = paste0(ownPath, "/group")

source(completeSource)