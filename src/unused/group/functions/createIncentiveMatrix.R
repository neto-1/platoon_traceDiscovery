
createIncentiveMatrix <- function(incentivesRValues,vehicles, configData) {
	

	vehicleList = vehicles
	
	## create initial and empty incentivesR-Matrix
	incentivesR <- array(0, dim=c(length(vehicleList),length(vehicleList), configData$numberoffunctions+1))

	# assign the values into the incentiveR matrix
	for (values in 1:length(incentivesRValues$veh1)) {
		incentivesR[which(vehicleList==incentivesRValues$veh1[values]),which(vehicleList==incentivesRValues$veh2[values]),1] = incentivesRValues$vector_deg[values]
		incentivesR[which(vehicleList==incentivesRValues$veh1[values]),which(vehicleList==incentivesRValues$veh2[values]),2] = incentivesRValues$gradient[values]
		incentivesR[which(vehicleList==incentivesRValues$veh1[values]),which(vehicleList==incentivesRValues$veh2[values]),3] = incentivesRValues$volumeOverlap[values]
		incentivesR[which(vehicleList==incentivesRValues$veh1[values]),which(vehicleList==incentivesRValues$veh2[values]),4] = incentivesRValues$areaOverlap[values]
	}
	
	

	### process of merging all values
	incentivesR[,,5] = (incentivesR[,,1] + incentivesR[,,2] + incentivesR[,,3] + incentivesR[,,4]) * 0.25
	
	# remove lower triangular matrix
	incentivesR[,,5][lower.tri(incentivesR[,,5])] <- 0
	
	return(incentivesR[,,5])
}


#print("ready-getMax")

#rm(list=ls())
