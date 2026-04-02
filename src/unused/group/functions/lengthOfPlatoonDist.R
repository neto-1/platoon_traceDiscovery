
lengthOfPlatoonDist <- function(x) {
	sum ( sqrt( (p12[1] - x[1])^2 + (p12[2] - x[2])^2 ) + sqrt( (p13[1] - x[1])^2 + (p13[2] - x[2])^2 ) + sqrt( (p22[1] - x[3])^2 + (p22[2] - x[4])^2 ) + sqrt( (p23[1] - x[3])^2 + (p23[2] - x[4])^2 ) + sqrt( (x[1] -x[3])^2 + (x[2] - x[4])^2 ) * lw)
}


#print("ready-lengthOfPlatoonDist")