library(yaml)
print("R: SD Algorithm")
args = commandArgs(trailingOnly=TRUE)

vehicles = (as.numeric(args[1]))
groups = (as.numeric(args[2]))
ownPath = args[3]
testid = (as.numeric(args[4]))

postfix = "/group/sd/"

LimitValue = vehicles
kGroups = groups
completeSource = paste0(ownPath,postfix,"sd.R")
ownPath = paste0(ownPath, "/group")

source(completeSource)
