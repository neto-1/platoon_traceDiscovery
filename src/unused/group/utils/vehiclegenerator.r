library(RNeo4j)
library(tictoc)
library(sp)
library(rgeos)
library(httr)
library(jsonlite)


tic()
graph = startGraph("http://localhost:7474/db/data/", username="neo4j", password="12345678")

# map <- cypher(graph,"MATCH (n:loc) RETURN n.location, n.lat AS lat, n.lon AS lon, id(n) AS id limit 1000")
# rels <- cypher(graph,"MATCH (n)-[r:NEIGHBOUR]->(m) RETURN n.lon, m.lon, n.lat, m.lat, id(r) as rid, id(n) as nid, id(m) as mid")

#rels <- cypher(graph, "MATCH p=(n)-[r:NEIGHBOUR]-(m) where r.type='motorway' RETURN n.lon, m.lon, n.lat, m.lat, id(r) as rid, id(n) as nid, id(m) as mid")
#rels <- cypher(graph, "MATCH p=(n)-[r:NEIGHBOUR]->(m) RETURN n.lon, m.lon, n.lat, m.lat, id(r) as rid, id(n) as nid, id(m) as mid")

# plot(map$lon,map$lat)
# for ( d in 1:length(rels$m.lon) ) {
	# lines(c(as.numeric(rels$n.lon[d]), as.numeric(rels$m.lon[d])),  c(as.numeric(rels$n.lat[d]), as.numeric(rels$m.lat[d])))
# }

# toc()

astr <- function(start,end) {
	user = "neo4j";
	pass = "12345678";
	auth = authenticate(user, pass, type = "basic")
	urla = "http://localhost:7474/RestAPI/PathFinderAPI/post"
	r <- POST(urla, 
	body = paste0('{
	   "start" :',start,',
	   "end" : ',end,',
	   "costProperty" : "distance",
	   "latProperty" : "lat",
	   "lonProperty" : "lon",
	   "types" : ["NEIGHBOUR"],
	   "nodeProperties": ["id", "lon", "lat"],
	   "relProperties" : ["distance", "id"],
	   "direction" : "both"
	}'), auth);
	
	
	json <- content(r, "text", encoding = "UTF-8")
	json <- (gsub("Node", "", json, ignore.case=FALSE, fixed=FALSE))
	
	
	
	if(validate(json)) {
		obj <- fromJSON(json)
	} else {
		return(NULL)
	}
	
	if(is.null(obj) || obj$length <= 0) {
		
		#print(paste(start,end))
		
		
		#print(obj)

		return(NULL)
	}

	len = obj$distance;
	spm <- array(0, dim=c(length(obj$nodes),4))
	for(d in 1:length(obj$nodes)) {
		item <- gsub(" ", "", (obj$nodes[[d]]))
		comma <- gregexpr(",", item)
		colon <- gregexpr(":", item)
		
		for(com in 1:length(colon[[1]])) {
			colonpos = colon[[1]][com]
			commapos = comma[[1]][com]
			if(!is.na(commapos)) {
				res = substr(item, colonpos+1, commapos-1)
			} else {
				res = substr(item, colonpos+1, nchar(item)-1)
			}
			spm[d,com]= res;
		}
		spm[d,4] = len
	}
	return(spm);
}


tic()
x = 0;
while(x < 1000) {
	startend <- cypher(graph, "MATCH (n:loc) WITH n, rand() AS number RETURN id(n) as n ORDER BY number LIMIT 2")
	
	num01 = startend[1,1]
	num02 = startend[2,1]

	print(num01)
	print(num02)
	
	
	path = (astr(num01,num02))
	distance = as.integer(path[1,4])

	if(length(distance) > 0 && distance >= 300) {
		print(distance)
		

		nodeid = as.integer(cypher(graph,"CREATE (n:veh) RETURN id(n)"))
		cypher(graph, paste("MATCH (v:veh), (l1:loc), (l2:loc) WHERE id(v)=",nodeid," and id(l1)=",num01," and id(l2)=",num02," CREATE (l1)<-[r1:STARTATLOCATION]-(v)-[r2:ENDATLOCATION]->(l2)"));
		x = x+1;
	}
}
toc()

