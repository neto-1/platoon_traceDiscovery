print("R run")
args = commandArgs(trailingOnly=TRUE)

vehicles = (as.numeric(args[1]))
groups = (as.numeric(args[2]))

LimitValue = vehicles
kGroups = groups
#LimitValue = 10

#ownPath = (script.dir <- dirname(sys.frame(1)$ofile))
#ownPath = "C:/Users/Dietrich/Documents/GIT/platoon/src/group/convex/"
#ownPath = "C:/Users/cg-admin/Documents/git/src/group/convex/"
ownPath = "C:/Users/cg-admin/Documents/Platooning/Git/src/group/sd/"

#ownPath = args[3]

#print(ownPath)
#ownPath = paste0(ownPath,"/group/convex/")
#completeSource = paste0(ownPath,"group/convex/main.r")
completeSource = paste0(ownPath,"main.r")

ownPath = "C:/Users/cg-admin/Documents/Platooning/Git/src/group/"
source(completeSource)