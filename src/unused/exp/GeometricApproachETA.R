
suppressWarnings(suppressMessages(library(jsonlite)))
suppressWarnings(suppressMessages(library(yaml)))
library(yaml)
library(jsonlite)
args = commandArgs(trailingOnly=TRUE)

p12 = c(as.numeric(args[2]), as.numeric(args[3]))
p13 = c(as.numeric(args[4]), as.numeric(args[5]))
p22 = c(as.numeric(args[6]), as.numeric(args[7]))
p23 = c(as.numeric(args[8]), as.numeric(args[9]))

lw= as.numeric(args[10])


lengthOfPlatoonDist <- function(x) {
	sum ( sqrt( (p12[1] - x[1])^2 + (p12[2] - x[2])^2 ) + sqrt( (p13[1] - x[1])^2 + (p13[2] - x[2])^2 ) + sqrt( (p22[1] - x[3])^2 + (p22[2] - x[4])^2 ) + sqrt( (p23[1] - x[3])^2 + (p23[2] - x[4])^2 ) + sqrt( (x[1] -x[3])^2 + (x[2] - x[4])^2 ) * (2-lw))
}

###### compute extended fermar weber points with gradient approach
g<-nlm(lengthOfPlatoonDist, x <- c(0,1,0,1), hessian=FALSE);
###### results of gradient computation

gresult <- g[2];
g1p <- c(gresult[[1]][1],gresult[[1]][2]);
g2p <- c(gresult[[1]][3],gresult[[1]][4]);

###### compute linear distance of compared vehicles
v1lin = p12 - p22
v1lin = sqrt( v1lin[1]^2 + v1lin[2]^2);
v2lin = p13 - p23;
v2lin = sqrt( v2lin[1]^2 + v2lin[2]^2);
singleLDis = v1lin + v2lin;

###### compute linear platooned distance of compared vehicles
s1lin = g1p - p12;
s1lin = sqrt( s1lin[1]^2 + s1lin[2]^2);
s2lin = g1p - p13;
s2lin = sqrt( s2lin[1]^2 + s2lin[2]^2);
glin = g1p - g2p;
glin = sqrt( glin[1]^2 + glin[2]^2 )
e1lin = g2p - p22;
e1lin = sqrt( e1lin[1]^2 + e1lin[2]^2);
e2lin = g2p - p23;
e2lin = sqrt( e2lin[1]^2 + e2lin[2]^2);
platoonedLDis = s1lin + s2lin + e1lin + e2lin + glin *(2-lw);


return_data = list(platoon_dist=platoonedLDis,air_dist=singleLDis, point=c(p12,p13,p22,p23), air=c(v1lin+v2lin,glin))
print(toJSON(return_data))
#print("ready-modifiedGeometricApproach")