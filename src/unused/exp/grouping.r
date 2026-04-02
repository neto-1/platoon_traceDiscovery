suppressWarnings(suppressMessages(library(gdata)))
suppressWarnings(suppressMessages(library(yaml)))
library(yaml)
library(gdata)
print("R: Convex Algorithm with Time")
args = commandArgs(trailingOnly=TRUE)


ownPath = args[1]
identifyGroupsBy = args[2]
groups = (as.numeric(args[3]))
setID = (as.numeric(args[4]))
#ownPath = "/Users/dmitry/Documents/wd/platooning/src"
postfix = "/group/convex/"

############################### Start file of the algorithm ###############################

############### parameters for mainTime ###############
# configSet="default"		### the considered config set
# identifyGroupsBy			### the type of grouping algorithm which is applied (e.g. "greedy")
############################################################


###### load the function ######
# source(paste0(ownPath,postfix,"mainTime.r"))

# set the working directionary to the group folder
setwd(paste0(ownPath, "/group/"))

# load the function of mainTime.r
completeSource = paste0(ownPath,postfix,"groupingVehicles.r")
source(completeSource)

###### run the function ######
## if the grouping is active, R will create groups out of incentives for the given parameter. else only one group will be created, which contains all vehicles of the considered set
returnOfMain = groupingVehicles(,identifyGroupsBy,groups,setID)

print(toJSON(returnOfMain))

#print(toString(returnOfMain))