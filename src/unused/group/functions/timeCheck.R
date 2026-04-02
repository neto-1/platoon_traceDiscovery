
timeCheck <- function(vehicles,timesAreConsidered) {
	
	###### check if there is always an early and a late time, if not early times will be set to late times and vice versa
	if(!("startEarly" %in% colnames(vehicles)) & ("startLate" %in% colnames(vehicles)) ) {
		vehicles = cbind(vehicles,"startEarly" = vehicles$startLate)
	}
	if(!("startLate" %in% colnames(vehicles)) & ("startEarly" %in% colnames(vehicles))) {
		vehicles = cbind(vehicles,"startLate" = vehicles$startEarly)
	}
	if(!("endEarly" %in% colnames(vehicles)) & ("endLate" %in% colnames(vehicles)) ) {
		vehicles = cbind(vehicles,"endEarly" = vehicles$endLate)
	}
	if(!("endLate" %in% colnames(vehicles)) & ("endEarly" %in% colnames(vehicles)) ) {
		vehicles = cbind(vehicles,"endLate" = vehicles$endEarly)
	}
	
	
	###### check if there are no times at all and the algorithm has to perform without times
	if(!("startEarly" %in% colnames(vehicles) & "startLate" %in% colnames(vehicles) & "endEarly" %in% colnames(vehicles) & "endLate" %in% colnames(vehicles))) {
		vehicles = cbind(vehicles,"noTime" = 0)
	}
	
	##### chick if times should be considered due to parameter "timesAreConsidered"
	if(!timesAreConsidered) {
		vehicles <- data.frame(vehicles$v1slon, vehicles$v1slat, vehicles$v1elon, vehicles$v1elat, vehicles$v1sid, vehicles$v1eid, vehicles$IDn, c(0))
		colnames(vehicles) <- c("v1slon", "v1slat", "v1elon", "v1elat", "v1sid", "v1eid", "IDn", "noTime")
	}
	
	return(vehicles)
}



#print("ready-timeCheck")


