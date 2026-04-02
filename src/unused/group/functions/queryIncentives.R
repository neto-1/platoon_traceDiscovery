
queryIncentives <- function(graph, configData) {
		
	# query for the pattern
	queryPattern = paste0('match (m:',configData$vehicle,')-[:',configData$vehiclePair,']-(u:',configData$vehPair,')-[:',configData$vehiclePair,']-(n:',configData$vehicle,') ')
	
	# query for the return
	queryReturn = paste0('RETURN u.vector_degree as vector_deg, u.gradient as gradient, u.overlapVol as volumeOverlap, u.overlapArea as areaOverlap, id(m) as veh1,id(n) as veh2, id(u) as IDu')
	### add the query up ###
	queryComplete = paste0(queryPattern,queryReturn)
	
	############ load the incentives and vehicle informations ############
	incentivesR <- cypher(graph, queryComplete) 
	
	return(incentivesR)
}

