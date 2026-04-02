library(RNeo4j)
library(tictoc)
library(sp)
library(rgeos)


graph = startGraph("http://localhost:7474/db/data/", username="neo4j", password="12345678")

#map <- cypher(graph,"MATCH (n)-[:group]-(g:Group) WHERE id(g) = 4050 RETURN n.location, n.lat AS lat, n.lon AS lon, id(n) AS id LIMIT 3000")
#rels <- cypher(graph,"MATCH  p=(n)-[r1:group]-(g:Group)-[r2:group]-(m) WHERE id(g) = 4050 WITH n,m MATCH pb = (n)-[r:NEIGHBOUR]-(m) RETURN n.lon, m.lon, n.lat, m.lat, id(r) as rid, id(n) as nid, id(m) as mid")


map <- cypher(graph,"MATCH (n:loc) RETURN n.location, n.lat AS lat, n.lon AS lon, id(n) AS id")
rels <- cypher(graph,"MATCH (n)-[r:NEIGHBOUR]->(m) RETURN n.lon, m.lon, n.lat, m.lat, id(r) as rid, id(n) as nid, id(m) as mid")
#map <- cypher(graph,"CALL spatial.bbox('geom',{lon:10,lat:53}, {lon:13, lat:61}) YIELD node  as n with n RETURN n.location, n.lat AS lat, n.lon AS lon, id(n) AS id LIMIT 3000")
#map <- cypher(graph,"WITH 'POLYGON((10 53, 10 54, 13 54, 13 53, 10 53))' as polygon CALL spatial.intersects('geom',polygon) YIELD node as n RETURN n.location, n.lat AS lat, n.lon AS lon, id(n) AS id LIMIT 3000")
#WITH 'POLYGON((10 53, 10 54, 13 54, 13 53, 10 53))' as polygon CALL spatial.intersects('geom',polygon) YIELD node RETURN node
#print(rels)

# map = rbind(map,c(NA, 51,6,34587934))
# map =rbind(map,c(NA,47,8,2343252))


plot(map$lon,map$lat)
print(map$lon)
groups <- cypher(graph, "MATCH (n:Group) WHERE id(n) = 4511 RETURN n.Poly as n LIMIT 1")

#print(groups$n[[1]][[1]])
# print(length(groups$n[[1]]))


coord = c();
for (i in 1:length(groups$n[[1]]) ) {
	coord <- c(coord,(groups$n[[1]][[i]]))
}


#coord = c(6.6, 49.1, 6.6,49.6, 7.2,49.6, 7.2,49.2,6.6, 49.1)
print(coord)



par(pch=22, col="red", lwd=1.8)
for ( i in 1:(length(coord)/2-1) ) {
	
	
	# indexpoint = ((i-1)*2+1)
	# if(index<(length(coord))) {
		# print(paste(coord[[indexpoint]], " ", coord[[indexpoint+1]]))
	# }
	as.numeric(coord[2])
	#lines(c(6.6,7),c(49,49.5))
	index = ((i-1)*2+1)
	print(index)

	#if(index<(length(coord)-2)) {
		print(paste(coord[[index]], coord[[index+2]],coord[[index+1]], coord[[index+3]]))
		#print(paste(coord[[i]], coord[[i+2]],coord[[i+1]], coord[[i+3]]))
		lines(c(as.numeric(coord[[index]]), as.numeric(coord[[index+2]])), c( as.numeric(coord[[index+1]]), as.numeric(coord[[index+3]])))
		
	#}
}
lines(c(as.numeric(coord[[length(coord)-1]]), as.numeric(coord[[1]])), c( as.numeric(coord[[length(coord)]]), as.numeric(coord[[2]])))


query = "WITH 'POLYGON(("
for (i in 1:length(coord) ) {
	query=paste(query, (coord[[i]]))
	if(i%%2 == 0 && i < length(coord)) {
		query=paste(query,", ")
	} 
}	

query = paste(query,"))' as polygon CALL spatial.intersects('geom',polygon) YIELD node as n RETURN n.location, n.lat AS lat, n.lon AS lon, id(n) AS id")

print(query)

#map <- cypher(graph,"WITH 'POLYGON((6 51, 7 52, 8 51, 7 51, 6 51))' as polygon CALL spatial.intersects('geom',polygon) YIELD node as n RETURN n.location, n.lat AS lat, n.lon AS lon, id(n) AS id LIMIT 3000")
map <- cypher(graph,query)


par(pch=22, col="red", lwd=1.8)
points(map$lon,map$lat)






# par(pch=22, col="gray", lwd=1.8)

# plot(map$lon,map$lat)
for ( d in 1:length(rels$m.lon) ) {
	#print(paste(as.numeric(rels$n.lon[d]), as.numeric(rels$m.lon[d]),  as.numeric(rels$n.lat[d]), as.numeric(rels$m.lat[d])))
	#lines(c(as.numeric(rels$n.lon[d]), as.numeric(rels$m.lon[d])),  c(as.numeric(rels$n.lat[d]), as.numeric(rels$m.lat[d])))
}

#WITH "POLYGON((10 53, 10 54, 13 54, 13 53, 10 53))" as polygon
#CALL spatial.intersects('geom',polygon) YIELD node RETURN node
