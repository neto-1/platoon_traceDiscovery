

###################=== INITIALISATION ===####################
suppressWarnings(suppressMessages(library(RNeo4j)))
suppressWarnings(suppressMessages(library(tictoc)))
suppressWarnings(suppressMessages(library(sp)))
suppressWarnings(suppressMessages(library(rgeos)))
suppressWarnings(suppressMessages(library(httr)))
suppressWarnings(suppressMessages(library(jsonlite)))
suppressWarnings(suppressMessages(library(igraph)))
suppressWarnings(suppressMessages(library(RPostgreSQL)))
suppressWarnings(suppressMessages(library(geometry)))
suppressWarnings(suppressMessages(library(config)))
suppressWarnings(suppressMessages(library(yaml)))
suppressWarnings(suppressMessages(library(itertools)))
suppressWarnings(suppressMessages(library(kernlab)))

library(RNeo4j)
library(tictoc)
library(sp)
library(rgeos)
library(httr)
library(jsonlite)
library(igraph)
#library(RMySQL)
library(RPostgreSQL) 
library(geometry)
library(config)
library(yaml)
library(itertools)
library(kernlab)


######################################## initially load the functions ########################################

functions = c("listToMatrix", "createIncentiveMatrix", "queryIncentives","storeIncentives", "greedyGroupCreating","spectralExtraGroupCreating","bronKerbosch","walktrap","spectralClustering","formingDisjointGroupsRm","storeVehicleHulls", "collectParameters", "spectralM", "inducedSubgraph", "astr", "vehConvexHullTime", "findLowestValue", "loadConfigSet", "queryVehicles", "timeCheck", "vehicleCompare", "neo4jInit", "vehConvexHull", "modifiedGeometricApproach", "modifiedGeometricApproachTime", "creatingGroupPoolMatrix", "compareVehVector", "compareVehVectorTime", "intersection", "intersectionTime", "lengthOfPlatoonDist", "getMax", "formingDisjointGroups", "formingNotDisjointGroups", "storeGroups")


##load the functions in the vector "functions"
for (func in 1:length(functions)) {
	functionname = functions[func]
	
	## convert the actual path and add the needed source path ######
	completeSource = paste0(getwd(),"/functions/",functionname, ".R")
	source(completeSource)
}
########################################################################################################################
