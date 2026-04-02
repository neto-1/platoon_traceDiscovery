

modifiedGeometricApproachTime <- function(vehicles, j, i, lw=0.5) {
	###################### STEP 2 - Extended Fermat Weber Problem ######################
	##Parameter
	
	
	p12 <- c(vehicles$v1slon[j], vehicles$v1slat[j], vehicles$startEarly[j]);
	p22 <- c(vehicles$v1elon[j], vehicles$v1elat[j], vehicles$endLate[j]);
	#p12 = start of veh 1
	#p22 = end of veh 1
	
	p13 <- c(vehicles$v1slon[i], vehicles$v1slat[i], vehicles$startEarly[i]);
	p23 <- c(vehicles$v1elon[i], vehicles$v1elat[i], vehicles$endLate[i]);
	#p13 = start of veh 2
	#p23 = end of veh 2

	lengthOfPlatoonDist <- function(x) {
		#sum ( sqrt( (p12[1] - x[1])^2 + (p12[2] - x[2])^2 ) + sqrt( (p13[1] - x[1])^2 + (p13[2] - x[2])^2 ) + sqrt( (p22[1] - x[3])^2 + (p22[2] - x[4])^2 ) + sqrt( (p23[1] - x[3])^2 + (p23[2] - x[4])^2 ) + sqrt( (x[1] -x[3])^2 + (x[2] - x[4])^2 ) * lw)
		sum ( (abs(p12[1] - x[1])^2 + abs(p12[2] - x[2])^2 + abs(p12[3] - x[3])^2)^(1/2) + (abs(p13[1] - x[1])^2 + abs(p13[2] - x[2])^2 + abs(p13[3] - x[3])^2)^(1/2) + (abs(p22[1] - x[4])^2 + abs(p22[2] - x[5])^2 + abs(p22[3] - x[6])^2 )^(1/2) + ( abs(p23[1] - x[4])^2 + abs(p23[2] - x[5])^2 + abs(p23[3] - x[6])^2 )^(1/2) + ( abs(x[1] - x[4])^2 + abs(x[2] - x[5])^2 + abs(x[3] - x[6])^2 )^(1/2) * lw)
	}
	
	
	#sum ( (abs(p12[1] - x[1])^3 + abs(p12[2] - x[2])^3 + abs(p12[3] - x[3])^3)^(1/3) + (abs(p13[1] - x[1])^3 + abs(p13[2] - x[2])^3 + abs(p13[3] - x[3])^3)^(1/3) + (abs(p22[1] - x[4])^3 + abs(p22[2] - x[5])^3 + abs(p22[3] - x[6])^3 )^(1/3) + ( abs(p23[1] - x[4])^3 + abs(p23[2] - x[5])^3 + abs(p23[3] - x[6])^3 )^(1/3) + ( abs(x[1] - x[4])^3 + abs(x[2] - x[5])^3 + abs(x[3] - x[6])^3 )^(1/3) * lw)
	#sum ( ((p12[1] - x[1])^3 + (p12[2] - x[2])^3 + (p12[3] - x[3])^3)^(1/3) + ((p13[1] - x[1])^3 + (p13[2] - x[2])^3 + (p13[3] - x[3])^3)^(1/3) + ((p22[1] - x[4])^3 + (p22[2] - x[5])^3 + (p22[3] - x[6])^3 )^(1/3) + ( (p23[1] - x[4])^3 + (p23[2] - x[5])^3 + (p23[3] - x[6])^3 )^(1/3) + ( (x[1] - x[4])^3 + (x[2] - x[5])^3 + (x[3] - x[6])^3 )^(1/3) * lw)
	
	
	###### compute extended fermar weber points with gradient approach
	g<-nlm(lengthOfPlatoonDist, x <- c(1,1,1,1,1,1), hessian=FALSE);
	###### results of gradient computation
	
	gresult <- g[2];
	g1p <- c(gresult[[1]][1],gresult[[1]][2],gresult[[1]][3]);
	g2p <- c(gresult[[1]][4],gresult[[1]][5],gresult[[1]][6]);
	
	###### compute linear distance of compared vehicles
	v1lin = p12 - p22
	v1lin = ( abs(v1lin[1])^2 + abs(v1lin[2])^2 + abs(v1lin[3])^2)^(1/2) ;
	v2lin = p13 - p23;
	v2lin = ( abs(v2lin[1])^2 + abs(v2lin[2])^2 + abs(v2lin[3])^2)^(1/2);
	singleLDis = v1lin + v2lin;
	
	###### compute linear platooned distance of compared vehicles
	s1lin = g1p - p12;
	s1lin = ( abs(s1lin[1])^2 + abs(s1lin[2])^2 +abs(s1lin[3])^2)^(1/2);
	s2lin = g1p - p13;
	s2lin = ( abs(s2lin[1])^2 + abs(s2lin[2])^2 +abs(s2lin[3])^2)^(1/2);
	glin = g1p - g2p;
	glin = ( abs(glin[1])^2 + abs(glin[2])^2 +abs(glin[3])^2)^(1/2)
	e1lin = g2p - p22;
	e1lin = ( abs(e1lin[1])^2 + abs(e1lin[2])^2 +abs(e1lin[3])^2)^(1/2)
	e2lin = g2p - p23;
	e2lin = ( abs(e2lin[1])^2 + abs(e2lin[2])^2 +abs(e2lin[3])^2)^(1/2)
	platoonedLDis = s1lin + s2lin + e1lin + e2lin + glin *(2-lw);

	#return the platooned distance and the distance of each vehicle
	return(c(platoonedLDis,singleLDis))
}





#save.image("thisfunction.model")



#rm(list=ls())


#print("ready-modifiedGeometricApproach")