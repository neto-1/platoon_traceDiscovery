
storeIncentives <- function(incentivesRAllValues, uploadtoNeo = TRUE, set_id, configData) {
	
	### store all values of incentives in neo4j
	
	# for every value in incentivesRAllValues a node should be created
	while (max(incentivesRAllValues[,,5]) > 0 ) {
		# id of vehicle 1
		veh1 = colnames(incentivesRAllValues[,,5])[getMax(incentivesRAllValues[,,5])[2]]
		
		# id of vehicle 2
		veh2 = colnames(incentivesRAllValues[,,5])[getMax(incentivesRAllValues[,,5])[1]]
		
		qry = paste0('create (g:',configData$vehPair,'{set_id: ',set_id ,',vector_degree: ',incentivesRAllValues[getMax(incentivesRAllValues[,,5])[2],getMax(incentivesRAllValues[,,5])[1],1],',gradient: ',incentivesRAllValues[getMax(incentivesRAllValues[,,5])[2],getMax(incentivesRAllValues[,,5])[1],2],',overlapVol: ',incentivesRAllValues[getMax(incentivesRAllValues[,,5])[2],getMax(incentivesRAllValues[,,5])[1],3],',overlapArea: ',incentivesRAllValues[getMax(incentivesRAllValues[,,5])[2],getMax(incentivesRAllValues[,,5])[1],4],'}) with g MATCH (n:',configData$vehicle,') where id(n) = ',veh1, ' OR id(n) = ',veh2, ' with n,g create (g)-[r:',configData$vehiclePair,']->(n)')
		
		if (uploadtoNeo) {
			cypher(graph,qry)
		}
		incentivesRAllValues[getMax(incentivesRAllValues[,,5])[2],getMax(incentivesRAllValues[,,5])[1],5] = 0
	}
	
	
##############################################################################################################################	
	return(NULL)
}


#print("ready-storeGroups")