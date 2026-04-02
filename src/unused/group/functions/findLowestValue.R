


findLowestValue <-function(incentivesR) {

	##### preparing the incentivesR for the computation of the groups
	# find lowest value in incentivesR, therefore set all entrys with 0 to a value of 1 (since we want to find the lowest value > 0)
	
	if (length(which(incentivesR > 0)) >0) {
		incentivesR[incentivesR == 0] <- 1
	
		#this value is the lowest in incentivesR without 0
		lowestValue = min(incentivesR)
	} else {
		lowestValue = 0
	}
	
	# return the value
	return(lowestValue)
}


#print("ready-findLowestValue")