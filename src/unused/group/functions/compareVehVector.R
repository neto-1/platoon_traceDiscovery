
compareVehVector <- function(vehicles,j,i) {
	
	p12 <- c(vehicles$v1slon[j], vehicles$v1slat[j]);
	p22 <- c(vehicles$v1elon[j], vehicles$v1elat[j]);
	
	p13 <- c(vehicles$v1slon[i], vehicles$v1slat[i]);
	p23 <- c(vehicles$v1elon[i], vehicles$v1elat[i]);
	
	pa = p22 - p12
	pb = p23 - p13
	
	LoCosines = (pa[1] * pb[1] + pa[2] * pb[2]) / ( sqrt((pa[1])^2+(pa[2])^2) * sqrt((pb[1])^2+(pb[2])^2) )
	
	return(LoCosines)
}

