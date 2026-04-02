# ToDo Describe input data (first param, second param)
vehicleCompare <- function(vehicles,configData,typeOfHull="convexHull",angleOfCos=0,savingFactorMedian=0.5,vectorComparison=1,gradientMethod=1,convexHull=1) {

	incentivesR <- array(0, dim=c(length(vehicles$v1slon),length(vehicles$v1slon), configData$numberoffunctions+1), dimnames = list(vehicles$IDn,vehicles$IDn,1:(configData$numberoffunctions+1)))
	
	for ( j in 1:(length(vehicles$v1slon)-1) ) { #1:length(vehicles$v1slon) ) {
		
		for ( i in j+1:length(vehicles$v1slon) ) {  #29:length(vehicles$v1slon) ) {
			if (i > length(vehicles$v1slon)) break
			
			########################## ===== STEPWISE ALGORITHM ===== ##########################
			###################### STEP 1 - 90 Degree Check ######################
			## check if times are considered and calculate the angles
			if (vectorComparison) {
				if("noTime" %in% colnames(vehicles)) {
					compareVehVectorx = compareVehVector(vehicles,j,i)
				} else {
					compareVehVectorx = compareVehVectorTime(vehicles,j,i)
				}
				## assign value in matrix or go to next vehicles
				if( compareVehVectorx < angleOfCos ) {
					if (i == length(vehicles$v1slon) || j == length(vehicles$v1slon)) break
					next
				} else {
					incentivesR[j,i,1] = compareVehVectorx 
				}
			} else {
				incentivesR[j,i,1] = 1
			}
			###################### STEP 2 - Extended Fermat Weber Problem ######################
			## check if times are considered and calculate the distances of platoon and single bee lines
			if (gradientMethod) {
				if("noTime" %in% colnames(vehicles)) {
					modifiedGeometricApproachx = modifiedGeometricApproach(vehicles,j,i,savingFactorMedian)
				} else {
					modifiedGeometricApproachx = modifiedGeometricApproachTime(vehicles,j,i,savingFactorMedian)
				}
				## assign value in matrix or go to next vehicles
				if(modifiedGeometricApproachx[2] <= modifiedGeometricApproachx[1] ) {
					if (i == length(vehicles$v1slon) || j == length(vehicles$v1slon)) break
					next
				} else {
					incentivesR[j,i,2] = (( modifiedGeometricApproachx[2] / modifiedGeometricApproachx[1]) -1) * ((2/savingFactorMedian)-1)
				}
			} else {
				incentivesR[j,i,2] = 1
			}
			
			###################### STEP 3 - Intersection ######################
			## check if times are considered, if yes calculate intersection in 2D, if not go to else and calculate vol and area
			if (convexHull) {
				if("noTime" %in% colnames(vehicles)) {
					Intersectionx = intersection(vehicles,j,i,configData)
					if( Intersectionx[length(Intersectionx)] <= 0 || is.null(intersection(vehicles,j,i,configData) ) ) {
					if (i == length(vehicles$v1slon) || j == length(vehicles$v1slon)) break
					next
					} else {
						incentivesR[j,i,3] = Intersectionx[length(Intersectionx)]
					}
				} else {
				
					intersectionTimex = intersectionTime(vehicles,j,i,configData,typeOfHull)
					
					intersecVol = (intersectionTimex[1] + intersectionTimex[3]) / (intersectionTimex[5] * 2)
					intersecArea = (intersectionTimex[2] + intersectionTimex[4]) / (intersectionTimex[6] * 2)
					if( intersectionTimex[length(intersectionTimex)] <= 0 || is.null(intersectionTime(vehicles,j,i,configData,typeOfHull) ) ) {
						if (i == length(vehicles$v1slon) || j == length(vehicles$v1slon)) break
						next
					} else {
						#incentivesR[j,i,3] = intersectionTime[length(intersectionTime)]
						incentivesR[j,i,3] = intersecVol
						incentivesR[j,i,4] = intersecArea
					}
				}
			} else {
				incentivesR[j,i,3] = 1
				incentivesR[j,i,4] = 1
			}
			
			
			###################### Agregate the values ######################
			if (vectorComparison | gradientMethod | convexHull) {
				if("noTime" %in% colnames(vehicles)) {
					incentivesR[j,i,4] = incentivesR[j,i,3] * incentivesR[j,i,1] * incentivesR[j,i,2]  #assign the two HDV for driving together
					incentivesR[j,i,5] = incentivesR[j,i,4]
				} else {
					#incentivesR[j,i,4] = (incentivesR[j,i,3] + incentivesR[j,i,1] + incentivesR[j,i,2]) /numberoffunctions #assign the two HDV for driving together
					incentivesR[j,i,5] = (incentivesR[j,i,4] + incentivesR[j,i,3] + incentivesR[j,i,1] + incentivesR[j,i,2])/4  #assign the two HDV for driving together
				}
			} else {
				incentivesR[j,i,5] = 1
			}
			if (i == length(vehicles$v1slon) || j == length(vehicles$v1slon)) break
			
			########################## ===== END - STEPWISE ALGORITHM ===== ##########################
			
		}
	}
	
	return(incentivesR)
}
