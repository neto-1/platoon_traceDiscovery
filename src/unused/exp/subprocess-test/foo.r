#!/usr/bin/env Rscript
install.packages("jsonlite", repos="http://cran.r-project.org", lib="./lib")
library("jsonlite", lib.loc="./lib")
args <- commandArgs(trailingOnly=TRUE)

# some long procedure
#Sys.sleep(3)
data <- list(system = args[1], desc = "Lorem ipsum dolor sit amet ..., \r\n ...consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.")
cat("some logging data \n\n which should not be returned\n\n")
print("some logging data \n\n which should not be returned\n\n")
#Sys.sleep(3)

# return some JSON information
print(toJSON(data))
