mainTime <- function(configSet="default",kGroups=10,LimitValue=20,blaueBedingung=FALSE,timesAreConsidered=TRUE, testid = -1, typeOfHull="convexHull",angleOfCos=0 , savingFactorMedian=0.5,setID=0,vectorComparison=1,gradientMethod=1,convexHull=1) {
	
	#########################################################=== INITIALISATION ===#########################################################
	###### output the actual start time of the algorithm ######
	print(Sys.time())
	
	###### load the path of the working directionary and load initial functions ######
	#####load the initialization file "Initialization.r"
	sourceOfInitializatin = paste0(getwd(),"/convex/Initialization.r")
	source(sourceOfInitializatin)
	

	## start time ##
	dbStartTime = assign("dbStartTime",as.numeric(Sys.time()), env = .GlobalEnv); 
	
	############## LOAD PARAMETERS ##############
	####load the config for the parameters
	configData <- loadConfigSet(configSet)
	
	##### passworts and username for the graph database of neo4J #####
	graph = neo4jInit(configData)
	
	### actual time running ###
	dbTime =  assign("dbTime",as.numeric(Sys.time()) - dbStartTime, env = .GlobalEnv); 
	
	delete_time = as.numeric(Sys.time())
	############## DELETE OLD "HELPING"-NODES FOR NEXT ITERATION ##############
	# delete all groups
	deleteGraphGroups = paste0("MATCH (n:",configData$Group,") DETACH DELETE n")
	cypher(graph,deleteGraphGroups)
	# delete all sets
	deleteGraphPolygons = paste0("MATCH (n:",configData$Polygon,") DETACH DELETE n")
	cypher(graph,deleteGraphPolygons)
	# delete all PlatooningUtilities
	deleteGraphPolygons = paste0("MATCH (n:",configData$vehPair,") DETACH DELETE n")
	cypher(graph,deleteGraphPolygons)
	delete_time = as.numeric(Sys.time()) - delete_time
	############## query for the relevant data to create vehicles ##############
	vehicles <- queryVehicles(graph, configData, setID)
	

	#### These are the start and end times for the vehicles. the data should be pulled also in the query!!!! (this is a temporary solution for testings)
	################## Times must be adjusted to NOT outweight the geografical length!  ##################
	###### WARNING - see above ######
	vehicles = cbind(vehicles,"startEarly" = 0)
	vehicles = cbind(vehicles,"startLate" = 0.0001)
	vehicles = cbind(vehicles,"endEarly" = 0.0005)
	vehicles = cbind(vehicles,"endLate" = 0.0006)
	######################################## Times must be adjusted to not outweight the geografical length!  ########################################
	
	### store the convex hulls of each vehicle ###
	storeVehicleHulls(vehicles,,configData)
	
	############## check if there are actual times considered or only one start and one end time ##############
	vehicles <- timeCheck(vehicles,timesAreConsidered)
	
	#########################################################=== MAIN LOOP ===#########################################################
	mainTime = assign("mainTime",as.numeric(Sys.time()), env = .GlobalEnv); 
	print(vectorComparison)
	print(gradientMethod)
	############## iterate all vehicles with the applied config in configData ##############
	# in vehicle compare are the three comparisons (vector, median and convexHull) where convexHull is displayed by 2 values
	incentivesRAllValues = vehicleCompare(vehicles,configData,typeOfHull,angleOfCos,savingFactorMedian,vectorComparison,gradientMethod,convexHull)
	
	mTime = assign("mTime",as.numeric(Sys.time()) - mainTime , env = .GlobalEnv); 
	# store all incentives as a node respectively in neo4j
	store_incentives = as.numeric(Sys.time())
	storeIncentives(incentivesRAllValues,,setID , configData)
	store_incentives = as.numeric(Sys.time()) - store_incentives

	time_data <- c(dbTime,delete_time,mTime,store_incentives)
	
	returnOfMain = list(time_data=time_data)
	
	return(returnOfMain)
	
}


mainFullGroup <- function(configSet="default",timesAreConsidered=TRUE,setID=0) {
	
	#########################################################=== INITIALISATION ===#########################################################
	
	###### load the path of the working directionary and load initial functions ######
	#####load the initialization file "Initialization.r"
	sourceOfInitializatin = paste0(getwd(),"/convex/Initialization.r")
	source(sourceOfInitializatin)
	dbStartTime = assign("dbStartTime",as.numeric(Sys.time()), env = .GlobalEnv); 
	############## LOAD PARAMETERS ##############
	####load the config for the parameters
	configData <- loadConfigSet(configSet)
	
	##### passworts and username for the graph database of neo4J #####
	graph = neo4jInit(configData)
	dbTime =  assign("dbTime",as.numeric(Sys.time()) - dbStartTime, env = .GlobalEnv); 
	
	delete_time = as.numeric(Sys.time())
	############## DELETE OLD "HELPING"-NODES FOR NEXT ITERATION ##############
	# delete all groups
	deleteGraphGroups = paste0("MATCH (n:",configData$Group,") DETACH DELETE n")
	cypher(graph,deleteGraphGroups)
	# delete all sets
	deleteGraphPolygons = paste0("MATCH (n:",configData$Polygon,") DETACH DELETE n")
	cypher(graph,deleteGraphPolygons)
	# delete all PlatooningUtilities
	deleteGraphPolygons = paste0("MATCH (n:",configData$vehPair,") DETACH DELETE n")
	cypher(graph,deleteGraphPolygons)
	delete_time = as.numeric(Sys.time()) - delete_time
	
	############## query for the relevant data to create vehicles ##############
	vehicles <- queryVehicles(graph, configData, setID)
	
	
	#### These are the start and end times for the vehicles. the data should be pulled also in the query!!!! (this is a temporary solution for testings)
	################## Times must be adjusted to NOT outweight the geografical length!  ##################
	###### WARNING - see above ######
	vehicles = cbind(vehicles,"startEarly" = 0)
	vehicles = cbind(vehicles,"startLate" = 0.1)
	vehicles = cbind(vehicles,"endEarly" = 0.5)
	vehicles = cbind(vehicles,"endLate" = 0.6)
	######################################## Times must be adjusted to not outweight the geografical length!  ########################################
	
	### store the convex hulls of each vehicle ###
	storeVehicleHulls(vehicles,,configData)
	
	############## check if there are actual times considered or only one start and one end time ##############
	vehicles <- timeCheck(vehicles,timesAreConsidered)
	
	
	############### create a group with all vehicles in it #################
	groupPool <- array(1,dim=(c(length(vehicles$IDn),1)),dimnames= list(vehicles$IDn ,c(1)) )
	
	
	#### upload the group to neo4J
	storeGroups(groupPool, vehicles, TRUE,configData)
	
}

