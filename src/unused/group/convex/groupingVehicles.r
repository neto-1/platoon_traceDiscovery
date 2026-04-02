groupingVehicles <- function(configSet="default", identifyGroupsBy="greedy",kGroups=10, setID=0) {
	
	
	init_time = as.numeric(Sys.time())
	
	############## LOAD PARAMETERS ##############
	### initiate all functions
	sourceOfInitializatin = paste0(getwd(),"/convex/Initialization.r")
	source(sourceOfInitializatin)
	
	
	####load the config for the parameters
	configData <- loadConfigSet(configSet)
	
	### initiate the graph database
	graph = neo4jInit(configData)
	
	
	## query the incentives
	incentivesRValues = queryIncentives(graph,configData)
	
	## quer the vehicles to get an order
	vehicles <- queryVehicles(graph, configData, setID)
	init_time = as.numeric(Sys.time()) - init_time
	
	
	# construct the incentivesR matrix
	incentivesR = createIncentiveMatrix(incentivesRValues,vehicles$IDn,configData)
	
	
	# measure the time to create the groups
	gTime = as.numeric(Sys.time())
	
	if (max(incentivesR) > 0) {
		# define a cancel condition for greedy
		cancelCondition <- findLowestValue(incentivesR)
		
		## collect all parameters for grouping
		groupCreatingParameters = collectParameters(configData, cancelCondition, kGroups, length(incentivesRValues$veh1), identifyGroupsBy)
		
		# create the groups
		groupPoolReturn = creatingGroupPoolMatrix(incentivesR, groupCreatingParameters)
		####the return is a list of the groupPool(groupPoolReturn[[1]]) and the alphaCut (groupPoolReturn[[2]])
		# set groupPool variable
		groupPool = groupPoolReturn[[1]]
		
		# set alphaCut from returned value
		alphaCut = groupPoolReturn[[2]]
		
		numberOfGroups = groupPoolReturn[[3]]
	} else {
		groupPool = matrix(1, nrow=length(vehicles$IDn), ncol=1)
		alphaCut = 0
		numberOfGroups = 1
	}

	# measure the finish time of the grouping
	geTime = as.numeric(Sys.time()) - gTime
	
	
	## upload the groups and polygons to neo4j
	upTime = as.numeric(Sys.time())
	storeGroups(groupPool, vehicles, TRUE,configData)
	upTime = as.numeric(Sys.time()) - upTime
	
	time_data <- c(init_time,geTime,upTime)
	
	returnOfMain = list(time_data=time_data,alphaCut=alphaCut)
	
	return(returnOfMain)
}

