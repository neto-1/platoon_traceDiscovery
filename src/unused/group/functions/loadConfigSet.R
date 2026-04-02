
loadConfigSet <-function(configSet) {
	
	if(!exists("configData") | !(config::is_active(configSet))) {
		Sys.setenv(R_CONFIG_ACTIVE = configSet)
		#assign the set of configs which should be loaded (if nothing is set,it is default)

		#load the config
		configData = config::get()
	}
	return(configData)
}


#print("ready-loadConfigset")