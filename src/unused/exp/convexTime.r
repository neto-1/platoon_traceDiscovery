#suppressWarnings(suppressMessages(library(yaml)))
library(yaml)
print("R: Convex Algorithm with Time")
args = commandArgs(trailingOnly=TRUE)


vehicles = (as.numeric(args[1]))
groups = (as.numeric(args[2]))
ownPath = args[3]
typeOfHull = args[4]
angleOfCos = as.numeric(args[5])
savingFactorMedian = as.numeric(args[6])
setID = as.numeric(args[7])
vectorComparison = as.numeric(args[8])
gradientMethod = as.numeric(args[9])
convexHull= as.numeric(args[10])
groupingAvtive = as.numeric(args[11])

#ownPath = "/Users/dmitry/Documents/wd/platooning/src"
postfix = "/group/convex/"

############################### Start file of the algorithm ###############################

############### parameters for mainTime ###############
# configSet="default"		### the considered config set
# kGroups=10				### number of groups to be computed
# vehicles=20				### number of vehicles to be considered
# distribution="normal"		### distribution of vehicles (normal, random, lognormal....)
# lw=1.5					### factor for geometric median approach
# blaueBedingung=FALSE		###### this is the condition for dima for the slicing later on
# timesAreConsidered		### if true times will be considered (and optionally customized), if false times will be ignored and calculation will be without them
# identifyGroupsBy			### the type of grouping algorithm which is applied (e.g. "greedy")
############################################################


###### load the function ######
# source(paste0(ownPath,postfix,"mainTime.r"))

# set the working directionary to the group folder
setwd(paste0(ownPath, "/group/"))

# load the function of mainTime.r
completeSource = paste0(ownPath,postfix,"mainTime.r")
source(completeSource)

###### run the function ######
## if the grouping is active, R will create groups out of incentives for the given parameter. else only one group will be created, which contains all vehicles of the considered set
if (groupingAvtive) {
	returnOfMain = mainTime(,groups,vehicles,,TRUE,,typeOfHull,angleOfCos,savingFactorMedian,setID,vectorComparison,gradientMethod,convexHull)
} else {
	mainFullGroup(,,setID)

}
print(toJSON(returnOfMain))

#print(toString(returnOfMain))