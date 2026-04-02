




 functions = c("compareVehVector","astr", "vehConvexHull", "lengthOfPlatoonDist", "getMax", "modifiedGeometricApproach", "formingDisjointGroups", "Intersection", "formingNotDisjointGroups", "storeGroups")
 
 
 ###### find the path of the actual file ######
	ownPath = (script.dir <- dirname(sys.frame(1)$ofile))
 
 
### Parameter
for (func in 1:length(functions)) {

	functionname = functions[func]
	


###### convert the actual path and add the needed source path ######
	completeSource = paste0(ownPath,"/functions/",functionname, ".R")
	source(completeSource)
}







