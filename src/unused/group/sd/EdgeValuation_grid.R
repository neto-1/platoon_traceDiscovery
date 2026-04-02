EdgeValuation<-function(ig,sid,eid,sid2,eid2,allNodesGraph,unionPolygon,sigma)
{
  sid=12
  eid=82
  sid2=39
  eid2=84
  sigma=43
  subgraphResult<-induced.subgraph(ig,V(ig))
  initPolygon<-FALSE
  #create the list of nodes
  nodeList <- data.frame(id=allNodesGraph[,3],lat=allNodesGraph[,1],lon=allNodesGraph[,2])
  if(!is.null(unionPolygon)) 
  {
	
    ppol = unionPolygon@polygons[[1]]
    polyg = ppol@Polygons
    
    #load all points geometrically
    punkte = cbind(as.numeric(allNodesGraph[,2]),as.numeric(allNodesGraph[,1]))
    pts= (SpatialPoints(punkte))
    
    #overlay the points of unionPolygon to all other points 
    overpoints = over(unionPolygon,pts,returnList = TRUE)
	if(length(overpoints[[1]])==0 ||length(overpoints[[1]])==1){
		return (list(0,distances(ig,sid,eid)[1],distances(ig,sid2,eid2)[1]))
	}
    #find the ID of all the nodes inside of the union "unionPolygon"
    for (allNodes in 1:length(overpoints[[1]])) 
    {
	  if(nodeList$id[overpoints[[1]][allNodes]]==0)
	  {
		initPolygon<-TRUE
	  }
      else if (allNodes == 1 || initPolygon) 
      {
        allNodesPolygon = nodeList$id[overpoints[[1]][allNodes] ]
		initPolygon<-FALSE
      }	
      else if(nodeList$id[overpoints[[1]][allNodes]] %in% V(ig))
      {
        allNodesPolygon = cbind(allNodesPolygon,nodeList$id[overpoints[[1]][allNodes]])
      }
    }
  }
  else
  {
    allNodesPolygon=cbind(nodeList$id)
  }
  #sg<-induced.subgraph(ig,allNodesPolygon[1,])
  sg<-induced.subgraph(ig,V(ig))
  
  distanceShortestPath1<-distances(ig,sid,eid)[[1]]
  distanceShortestPath2<-distances(ig,sid2,eid2)[[1]]
  
  shortPath1 <- get.shortest.paths(ig, sid, eid)
  print(shortPath1$vpath[[1]])
  shortPath2 <- get.shortest.paths(ig,sid2, eid2)
  print(shortPath2$vpath[[1]])
  sigmaEdges<-matrix(0, nrow=length(nodelist[[1]]), ncol=2)
  count<-1
  par(pch=22, col="red",lwd=3)
  for ( i in 1:length(shortPath1$vpath[[1]]) ) {
    ind <- which(V(ig)==shortPath1$vpath[[1]][i]$name, arr.in=TRUE)
    points(as.numeric(vertex_attr(ig, "lon")[ind]), as.numeric(vertex_attr(ig, "lat")[ind]))
  }
  for ( i in 1:(length(shortPath1$vpath[[1]])-1) ) {
    ind <- which(V(ig)==shortPath1$vpath[[1]][i]$name, arr.in=TRUE)
    ind1 <- which(V(ig)==shortPath1$vpath[[1]][i+1]$name, arr.in=TRUE)
    lines(c(as.numeric(vertex_attr(ig, "lon")[ind]), as.numeric(vertex_attr(ig, "lon")[ind1])), c(as.numeric(vertex_attr(ig, "lat")[ind]), as.numeric(vertex_attr(ig, "lat")[ind1])))
  }
  par(pch=22, col="blue",lwd=3)
  for ( i in 1:length(shortPath2$vpath[[1]]) ) {
    ind <- which(V(ig)==shortPath2$vpath[[1]][i]$name, arr.in=TRUE)
    points(as.numeric(vertex_attr(ig, "lon")[ind]), as.numeric(vertex_attr(ig, "lat")[ind]))
  }
  for ( i in 1:(length(shortPath2$vpath[[1]])-1) ) {
   ind <- which(V(ig)==shortPath2$vpath[[1]][i]$name, arr.in=TRUE)
    ind1 <- which(V(ig)==shortPath2$vpath[[1]][i+1]$name, arr.in=TRUE)
    lines(c(as.numeric(vertex_attr(ig, "lon")[ind]), as.numeric(vertex_attr(ig, "lon")[ind1])), c(as.numeric(vertex_attr(ig, "lat")[ind]), as.numeric(vertex_attr(ig, "lat")[ind1])))
  }
  
  # for the nodes on the shortest path for vehicle 1 create sigma1
  vNormal <- (1/(sigma*sqrt(2*pi)))*exp(0)
  for ( i in 1:length(shortPath1$vpath[[1]])) {
    
    ind <- which(V(ig)==shortPath1$vpath[[1]][i]$name, arr.in=TRUE)
    if (is.null(vertex_attr(ig, "sigma1")[ind]) || is.na(vertex_attr(ig, "sigma1")[ind]) || (vertex_attr(ig, "sigma1")[ind] < vNormal)) {
      ig <- set.vertex.attribute(ig, "sigma1", index=ind, value=vNormal)
    }
  }
  
  # for the nodes on the shortest for vehicle 2 create sigma2
  for ( i in 1:length(shortPath2$vpath[[1]]) ) {
    ind <- which(V(ig)==shortPath2$vpath[[1]][i]$name, arr.in=TRUE)
    if (is.null(vertex_attr(ig, "sigma2")[ind]) || is.na(vertex_attr(ig, "sigma2")[ind]) || (vertex_attr(ig, "sigma2")[ind] < vNormal)) {
      ig <- set.vertex.attribute(ig, "sigma2", index=ind, value=vNormal)
    }
  }
	# for the nodes in the neighbourhood in ConvexHull
	for(j in 1:length(V(sg))) {

		ind <- which(V(ig) == V(sg)[j], arr.in = TRUE)

		minDistanceVehicle1<-min(distances(ig,V(ig)[ind],shortPath1$vpath[[1]]))
		minDistanceVehicle2<-min(distances(ig,V(ig)[ind],shortPath2$vpath[[1]]))
		# Normaldistribution
		vVehicle1<-1/(sigma*sqrt(2*pi))*exp(-minDistanceVehicle1/(2*sigma))^2
		vVehicle2<-1/(sigma*sqrt(2*pi))*exp(-minDistanceVehicle2/(2*sigma))^2
		
		if(length(ind)>0){
			if (is.null(vertex_attr(ig, "sigma1")[ind]) || is.na(vertex_attr(ig, "sigma1")[ind]) || (vertex_attr(ig, "sigma1")[ind] < vVehicle1)) {
				ig <- set.vertex.attribute(ig, "sigma1", index=ind, value=vVehicle1)
			}
			if(is.null(vertex_attr(ig, "sigma2")[ind]) || is.na(vertex_attr(ig, "sigma2")[ind]) || (vertex_attr(ig, "sigma2")[ind] < vVehicle2)){
				ig <- set.vertex.attribute(ig, "sigma2", index=ind, value=vVehicle2)
			}
			if (!is.null(vertex_attr(ig, "sigma2")[ind]) && !is.na(vertex_attr(ig, "sigma2")[ind]) && !is.null(vertex_attr(ig, "sigma1")[ind]) && !is.na(vertex_attr(ig, "sigma1")[ind]) && vertex_attr(ig, "sigma2")[ind]+vertex_attr(ig, "sigma1")[ind] > vNormal) {
				v = vertex_attr(ig, "sigma2")[ind]+vertex_attr(ig, "sigma1")[ind]
				ig <- set.vertex.attribute(ig, "sumsigma", index=ind, value=v)
				# reduce weight of neighbour-edges of the nodes with best sums
				if(!(incident(ig,ind) %in% sigmaEdges)) {
					sigmaEdges[count][1]<- incident(ig,ind)
					sigmaEdges[count,2]<-v
					weight<-(sigmaEdges[count,2]/vNormal)-1
					ig <- set.edge.attribute(ig, "weight", index=count, value=edge_attr(ig, "weight")*(1-weight))
					count = count+1
				}
			}
		}
    }
  shortPathMod1 <- get.shortest.paths(ig, sid, eid)
  shortPathMod2 <- get.shortest.paths(ig, sid2, eid2)
  print(shortPathMod1$vpath[[1]])
  print(shortPathMod2$vpath[[1]])
  par(pch=22, col="green",lwd=3)
  for ( i in 1:length(shortPathMod1$vpath[[1]]) ) {
    ind <- which(V(ig)==shortPathMod1$vpath[[1]][i]$name, arr.in=TRUE)
    points(as.numeric(vertex_attr(ig, "lon")[ind]), as.numeric(vertex_attr(ig, "lat")[ind]))
  }
  for ( i in 1:(length(shortPathMod1$vpath[[1]])-1) ) {
    ind <- which(V(ig)==shortPathMod1$vpath[[1]][i]$name, arr.in=TRUE)
    ind1 <- which(V(ig)==shortPathMod1$vpath[[1]][i+1]$name, arr.in=TRUE)
    lines(c(as.numeric(vertex_attr(ig, "lon")[ind]), as.numeric(vertex_attr(ig, "lon")[ind1])), c(as.numeric(vertex_attr(ig, "lat")[ind]), as.numeric(vertex_attr(ig, "lat")[ind1])))
  }
  par(pch=22, col="yellow",lwd=3)
  for ( i in 1:length(shortPathMod2$vpath[[1]]) ) {
    ind <- which(V(ig)==shortPathMod2$vpath[[1]][i]$name, arr.in=TRUE)
    points(as.numeric(vertex_attr(ig, "lon")[ind]), as.numeric(vertex_attr(ig, "lat")[ind]))
  }
  for ( i in 1:(length(shortPathMod2$vpath[[1]])-1) ) {
   ind <- which(V(ig)==shortPathMod2$vpath[[1]][i]$name, arr.in=TRUE)
    ind1 <- which(V(ig)==shortPathMod2$vpath[[1]][i+1]$name, arr.in=TRUE)
    lines(c(as.numeric(vertex_attr(ig, "lon")[ind]), as.numeric(vertex_attr(ig, "lon")[ind1])), c(as.numeric(vertex_attr(ig, "lat")[ind]), as.numeric(vertex_attr(ig, "lat")[ind1])))
  }
  shortPathMod1List<-cbind(shortPathMod1$vpath[[1]])
  shortPathMod2List<-cbind(shortPathMod2$vpath[[1]])
  intersection<-intersect(shortPathMod1List,shortPathMod2List)
  
  indSid <- which(V(subgraphResult)$name==sid, arr.in=TRUE)
  indEid <- which(V(subgraphResult)$name==eid, arr.in=TRUE)
  indSid2 <- which(V(subgraphResult)$name==sid2, arr.in=TRUE)
  indEid2 <- which(V(subgraphResult)$name==eid2, arr.in=TRUE)
  
  if(!is.null(intersection)&&!is.na(intersection)&&length(intersection)>0){
	  mergePoint<-intersection[1]
	  splitPoint<-tail(intersection,1)
	  indMerge<-which(V(subgraphResult)$name==mergePoint, arr.in=TRUE)
	  indSplit<-which(V(subgraphResult)$name==splitPoint, arr.in=TRUE)
	  distanceStartMergeVehicle1<-distances(subgraphResult,V(subgraphResult)[indSid],V(subgraphResult)[indMerge])[1]
	  distanceStartMergeVehicle2<-distances(subgraphResult,V(subgraphResult)[indSid2],V(subgraphResult)[indMerge])[1]
	  distanceMergeSplit<-distances(subgraphResult,V(subgraphResult)[indMerge],V(subgraphResult)[indSplit])[1]
	  distanceSplitEndVehicle1<-distances(subgraphResult,V(subgraphResult)[indSplit],V(subgraphResult)[indEid])[1]
	  distanceSplitEndVehicle2<-distances(subgraphResult,V(subgraphResult)[indSplit],V(subgraphResult)[indEid2])[1]
	  qualityValue<-(distanceStartMergeVehicle1+distanceStartMergeVehicle2+distanceMergeSplit*0.9+distanceMergeSplit+distanceSplitEndVehicle1+distanceSplitEndVehicle2)/(distanceShortestPath1+distanceShortestPath2)
	  if(qualityValue>1){
		qualityValue=0
	  }
	  print(qualityValue)
  }
  else{
	qualityValue<-0
  }
  if(qualityValue==0){
  distanceShortestPath1<-distances(subgraphResult,V(subgraphResult)[indSid],V(subgraphResult)[indEid])[1]
  distanceShortestPath2<-distances(subgraphResult,V(subgraphResult)[indSid2],V(subgraphResult)[indEid2])[1]
  }
  else{
	distanceShortestPath1<-distanceStartMergeVehicle1+distanceMergeSplit+distanceSplitEndVehicle1
	distanceShortestPath2<-distanceStartMergeVehicle2+distanceMergeSplit+distanceSplitEndVehicle2
  }
  print(distanceShortestPath1)
  print(distanceShortestPath2)
  return (list(qualityValue,distances(ig,sid,eid)[1],distances(ig,sid2,eid2)[1]))
}
