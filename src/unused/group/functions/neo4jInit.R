## does not need input arguments


neo4jInit <-function(configData) {
	#initiate the neo4j database
	config <- config::get()
	### the auth variable, which holds the password and username
	#needs to be global, so that i can be used in other functions
	
	pass = configData$password
	
	user = configData$username
	url = configData$url
	assign("auth", authenticate(user, pass, type = "basic"),env = .GlobalEnv)
	# the graph itself
	graph = assign("graph",startGraph(url, username=user, password=pass),env = .GlobalEnv)
	
	
	return(graph)
}


#print("ready-neo4jInit")