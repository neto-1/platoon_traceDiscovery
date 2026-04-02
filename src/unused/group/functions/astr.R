
astr <- function(start,end) {
	urla = "http://localhost:7474/RestAPI/PathFinderAPI/post"
	r <- POST(urla, 
	body = paste0('{
	   "start" :',start,',
	   "end" : ',end,',
	   "costProperty" : "distance",
	   "latProperty" : "lat",
	   "lonProperty" : "lon",
	   "types" : ["NEIGHBOUR","NEWN"],
	   "nodeProperties": ["id", "lon", "lat"],
	   "relProperties" : ["distance", "id", "type"],
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


#print("ready-astr")