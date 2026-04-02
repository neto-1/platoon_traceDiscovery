server <- function(){
  while(TRUE){
    writeLines("Listening...")
    con <- socketConnection(host="127.0.0.1", port = 5005, blocking=FALSE,
                            server=TRUE, open="r+")
    data <- readLines(con, 1)
    print(data)
    response <- toupper(data) 
    writeLines(response, con) 
    close(con)
  } 
}
server()