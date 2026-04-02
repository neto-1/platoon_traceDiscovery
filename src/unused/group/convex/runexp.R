
############################### Start file of the algorithm ###############################

############### parameters for mainTime ###############
# configSet="default"		### the considered config set
# kGroups=10				### number of groups to be computed
# vehicles=20				### number of vehicles to be considered
# skip=0					### skip ids of vehicles
# lw=1.5					### factor for geometric median approach
# blaueBedingung=FALSE		###### this is the condition for dima for the slicing later on
# timesAreConsidered		### if true times will be considered (and optionally customized), if false times will be ignored and calculation will be without them
# testid					### ID of the test
# identifyGroupsBy			### the type of grouping algorithm which is applied (e.g. "greedy")
# typeOfHull				### the type of convex Hull for the vehicles ("elipse","convexHull")
############################################################


#################################### DELETE FROM HERE TO 2354235347
# identifyGroupsBy			### which algorithm should be applied to form the groups out of the incentivesR (int value)
	# greedy: greedy algorithm to find groups
	# sp: spectal cluster
	# wtp: walktrap Partitioning
	# cl: clique
######################################################################## 2354235347
	
typeOfHull = "convexHull"
############################################################
#setwd(paste0(getwd(),"/platooning/src/group"))

###### load the function ######
source(paste0(getwd(),"/convex/mainTime.r"))


setID = 3430



###### run the function ######
mainTime(configSet="default",,,,,,,,,setID,,,)






# ############################### Start file of the algorithm ###############################
# library(gdata)
# ############### parameters for mainTime ###############
# # configSet="default"		### the considered config set
# # kGroups=10				### number of groups to be computed
# # vehicles=20				### number of vehicles to be considered
# # skip=0					### skip ids of vehicles
# # lw=1.5					### factor for geometric median approach
# # blaueBedingung=FALSE		###### this is the condition for dima for the slicing later on
# # timesAreConsidered		### if true times will be considered (and optionally customized), if false times will be ignored and calculation will be without them
# # testid					### ID of the test
# # identifyGroupsBy			### the type of grouping algorithm which is applied (e.g. "greedy")
# # typeOfHull				### the type of convex Hull for the vehicles ("elipse","convexHull")
# ############################################################


# #################################### DELETE FROM HERE TO 2354235347
# # identifyGroupsBy			### which algorithm should be applied to form the groups out of the incentivesR (int value)
	# # greedy: greedy algorithm to find groups
	# # sp: spectal cluster
	# # wtp: walktrap Partitioning
	# # cl: clique
# ######################################################################## 2354235347




# typeOfHull = "convexHull"
# ############################################################
# #setwd(paste0(getwd(),"/platooning/src/group"))

# ###### load the function ######
source(paste0(getwd(),"/convex/groupingVehicles.r"))

# ###### run the function ######
groupingVehicles(configSet="default", identifyGroupsBy="greedy",kGroups=10,setID)