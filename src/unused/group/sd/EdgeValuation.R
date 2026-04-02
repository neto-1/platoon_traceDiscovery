EdgeValuation<-function(ig,sid,eid,sid2,eid2,allNodesGraph,unionPolygon,sigma)
{
  
  initPolygon<-FALSE
  #create the list of nodes
  subgraphResult<-induced.subgraph(ig,V(ig))
  nodeList <- cbind(as.numeric(allNodesGraph[,4]))
  if(!is.null(unionPolygon)) 
  {
	
    ppol = unionPolygon@polygons[[1]]
    polyg = ppol@Polygons
    
    #load all points geometrically
    punkte = cbind(as.numeric(allNodesGraph[,3]),as.numeric(allNodesGraph[,2]))
    pts= (SpatialPoints(punkte))
    
    #overlay the points of unionPolygon to all other points 
    overpoints = over(unionPolygon,pts,returnList = TRUE)
	if(length(overpoints[[1]])==0 ||length(overpoints[[1]])==1){
		return (0)
	}
    #find the ID of all the nodes inside of the union "unionPolygon"
    for (allNodes in 1:length(overpoints[[1]])) 
    {
	  if(nodeList[overpoints[[1]][allNodes],1]==0)
	  {
		initPolygon<-TRUE
	  }
      else if (allNodes == 1 || initPolygon) 
      {
        allNodesPolygon = nodeList[overpoints[[1]][allNodes],1]
		initPolygon<-FALSE
      }	
      else if(nodeList[overpoints[[1]][allNodes],1] %in% V(ig))
      {
        allNodesPolygon = cbind(allNodesPolygon,nodeList[overpoints[[1]][allNodes],1])
      }
    }
  }
  else
  {
    allNodesPolygon=cbind(nodeList[,1])
  }
  if(length(allNodesPolygon[1,])==1 ||length(allNodesPolygon[1,])==0){
	return (0)
  }
  sg<-induced.subgraph(ig,allNodesPolygon[1,])
  
  indSid <- which(V(ig)$name==sid, arr.in=TRUE)
  indEid <- which(V(ig)$name==eid, arr.in=TRUE)
  indSid2 <- which(V(ig)$name==sid2, arr.in=TRUE)
  indEid2 <- which(V(ig)$name==eid2, arr.in=TRUE)
  
  distanceShortestPath1<-distances(ig,V(ig)[indSid],V(ig)[indEid])[[1]]
  distanceShortestPath2<-distances(ig,V(ig)[indSid2],V(ig)[indEid2])[[1]]
  
  shortPath1 <- get.shortest.paths(ig, V(ig)[indSid],V(ig)[indEid])
  shortPath2 <- get.shortest.paths(ig,V(ig)[indSid2],V(ig)[indEid2])
  sigmaEdges<-matrix(0, nrow=length(nodelist[[1]]), ncol=2)
  count<-1
  
  # for the nodes on the shortest path for both vehicles
  vNormal <- (1/(sigma*sqrt(2*pi)))*exp(0)

	# for the nodes in the neighbourhood in ConvexHull
	lengthSg<-length(V(sg))
	distance1<-distances(ig,V(ig),shortPath1$vpath[[1]])
	distance2<-distances(ig,V(ig),shortPath2$vpath[[1]])

	for (i in 1:lengthSg)
	{
	  ind <- which(V(ig)$name == V(sg)[i]$name, arr.in = TRUE)
	  minDistanceVehicle1<-min(distance1[ind,])
	  minDistanceVehicle2<-min(distance2[ind,])
	  # Normaldistribution
	  vVehicle1<-1/(sigma*sqrt(2*pi))*exp(-minDistanceVehicle1/(2*sigma))^2
	  vVehicle2<-1/(sigma*sqrt(2*pi))*exp(-minDistanceVehicle2/(2*sigma))^2
	  
	  if(length(ind)>0){
	     if(vNormal>vVehicle1 && vNormal>vVehicle2 && vVehicle1+vVehicle2>vNormal){
	      v = vVehicle1+vVehicle2
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
	
  shortPathMod1 <- get.shortest.paths(ig, V(ig)[indSid],V(ig)[indEid])
  shortPathMod2 <- get.shortest.paths(ig, V(ig)[indSid2],V(ig)[indEid2])

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
	  
	  qualityValue<-(distanceShortestPath1+distanceShortestPath2)/(distanceStartMergeVehicle1+distanceStartMergeVehicle2+distanceMergeSplit*0.9+distanceMergeSplit+distanceSplitEndVehicle1+distanceSplitEndVehicle2)
	  
	  if(qualityValue>1){
		qualityValue=1-qualityValue
	  }
	  
  }
  else{
	qualityValue<-0
  }
  if(is.null(qualityValue) ||is.na(qualityValue)){
	qualityValue<-0
  }
  print(qualityValue)
  return (qualityValue)
}
