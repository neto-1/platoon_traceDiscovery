scoreMatrixOutput <- function(configSet="default",kGroups=10,LimitValue=20,skip=30,lw=1.5,blaueBedingung=FALSE,timesAreConsidered=TRUE) {
	dbStartTime=0
	########################################### == LOAD PARAMETERS == ###########################################
	####load the config for the parameters
	configData <- loadConfigSet(configSet)
	
	############################## passworts and username for the graph database of neo4J ##############################
	graph = neo4jInit(configData)
	
	########################################################################################################################
	dbStartTime = assign("dbStartTime",as.numeric(Sys.time()), env = .GlobalEnv); 
	dbTime =  assign("dbTime",as.numeric(Sys.time()) - dbStartTime, env = .GlobalEnv); 
	toc() #34582

	######################################## DELETE GROUPS FOR NEXT ITERATION ########################################
	deleteGraphGroups = paste0("MATCH (n:",configData$Group,") DETACH DELETE n")
	cypher(graph,deleteGraphGroups)
	
	######################################## query for the relevant data to create vehicles ########################################
	vehicles <- queryVehicles(graph, configData, skip, LimitValue)
	
	
	#### These are the start and end times for the vehicles. the data should be pulled also in the query!!!! (this is a temporary solution for testings)
	################## Times must be adjusted to not outweight the geografical length!  ##################
	###### WARNING - see above ######
	vehicles = cbind(vehicles,"startEarly" = 0)
	vehicles = cbind(vehicles,"startLate" = 0.1)
	vehicles = cbind(vehicles,"endEarly" = 0.5)
	vehicles = cbind(vehicles,"endLate" = 0.6)
	######################################## Times must be adjusted to not outweight the geografical length!  ########################################

	######################################## check if there are actual times considered or only one start and one end time ########################################
	vehicles <- timeCheck(vehicles,timesAreConsidered)
	
	###############################################=== MAIN LOOP ===###############################################
	tic() # time needed to iterate the vehicle combinations #34564568
	mainTime = assign("mainTime",as.numeric(Sys.time()), env = .GlobalEnv); 
	
	############## iterate all vehicles in vehicles with the applied config in configData ##############
	matrixOfIntersectionQuality = vehicleCompare(vehicles,configData)
	

	mTime = assign("mTime",as.numeric(Sys.time()) - mainTime , env = .GlobalEnv); 
	toc() #34564568
	
	returnValue <- list(matrixOfIntersectionQuality,vehicles,configData)
	
	return(returnValue)
}
	
################# ===== >> === the lines which must be applied, when this function is used in mainTime() === << ===== #################

# # ##### run the main part: return vehicles (the list of vehicles and their attributes) and matrixOfIntersectionQuality (the matrix of incentives)
# # returnedValue <- scoreMatrixOutput(configSet,kGroups,LimitValue,skip,lw,blaueBedingung,timesAreConsidered)
# # #### set the returnedValue to matrixOfIntersectionQuality and vehicles
# # matrixOfIntersectionQuality <- returnedValue[[1]]
# # vehicles <- returnedValue[[2]]
# # configData <- returnedValue[[3]]
########################################################################################################################################