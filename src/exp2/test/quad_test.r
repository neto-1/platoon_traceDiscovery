if (!require(scmamp)) install.packages('scmamp')
library(scmamp)
library(multcompView)
library(xtable)
library(stringr)

data = read.csv("quade.csv")
#data = read.csv("quade_reduced.csv")

data <- as.matrix(data)

print(data)
# result <- quadeTest(data)
# print(result)
result <- quadePost(data, control=5)
print(result)

res <- postHocTest (data=data, use.rank=TRUE, test="quade", correct="finner")
print(res)

quad_latex = xtable(result, digits=2)
print(quad_latex)

print("=========")

result <- postHocTest(data, test = "friedman", use.rank=TRUE, correct="bergmann")
#print(result)
print(result$corrected.pval)



latex_result = xtable(result$corrected.pval, digits=3)
print(latex_result)

compare <- multcompLetters(result$corrected.pval, threshold=0.05)

print(compare)
