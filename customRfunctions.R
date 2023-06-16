# This is just a function list / help page for things that I find myself using quite a bit.

#rm(list=ls())
#setwd("~/Desktop/")

# how to use:
#library(devtools)
#source_url("https://raw.githubusercontent.com/syaheed/public-code/master/customRfunctions.R")

# custom functions:
rowsplit = function(x,column = 0, sp= "_"){
# splits rows of strings into a matrix based on a seperator (sp), and either returns the whole matrix (column = 0), or a particular column
  temp = do.call(rbind,strsplit(x,sp))
  if(column == 0){return(temp)}
  if(column > 0){return(temp[,column])}
}

pairedTest = function(x1,x2, name = "Condition"){
  # Does a bunch of paired statistics on x1 and x2, outputs a data.frame row
  # Example Use case: 
  #d1 = pairedTest(rnorm(30,0,1),rnorm(30,0,1),"case1")
  #d2 = pairedTest(rnorm(30,0,1),rnorm(30,2,1),"case2")
  #d = rbind(d1,d2)
  require("BayesFactor"); require("effsize"); require("pwr")
  cc = complete.cases(x1,x2)
  x1 = x1[cc] ; x2 = x2[cc]
  n = length(x1)
  n_increase = sum(x2 > x1) ; n_decrease = sum(x2 < x1)
  m1 = mean(x1) ; m2 = mean(x2)
  sd1 = sd(x1) ; sd2 = sd(x2)
  se1 = sd1/sqrt(n) ; se2 = se1/sqrt(n)
  wil = wilcox.test(x2, x1, paired = TRUE, exact=FALSE)
  wv = wil$statistic  
  wpval = wil$p.value  
  t = t.test(x2,x1, paired = TRUE, alternative = "two.sided")
  tstat = as.numeric(t$statistic)
  tpval = as.numeric(t$p.value)
  cohenD = cohen.d(x2,x1, paired=TRUE, hedges.correction=FALSE)$estimate
  hedgeG = cohen.d(x2,x1, paired=TRUE, hedges.correction=TRUE)$estimate  
  BF = ttestBF(x2,x1,paired = TRUE) ; BF = as.vector(BF)[[1]]
  reqSample = pwr.t.test(n = NULL, d = cohenD, sig.level = 0.05, power = 0.8, type = "paired", alternative = "two.sided")$n
  power = pwr.t.test(n = length(x1), d = cohenD, sig.level = 0.05, power = NULL, type = "paired", alternative = "two.sided")$power
  d = data.frame(name,n,n_increase,n_decrease,m1,m2,sd1,sd2,se1,se2,tstat,tpval,wv,wpval,cohenD,hedgeG,power,reqSample,BF)
  rownames(d) = NULL
  return(d)
}

pairedPlot = function(x1,x2, labels = c("x1","x2")){
  # does a paired plot of x1 and x2, along with providing the t-test results in the title
  cc = complete.cases(x1,x2); x1 = x1[cc]; x2 = x2[cc]
  t = t.test(x1,x2,paired = TRUE); stat = paste0('t = ', round(t$estimate,3), ', p = ', round(t$p.value,3))                               
  plot(-10,-10, xlim = c(0.5,2.5), ylim=c(min(c(x1,x2)),max(c(x1,x2))), xlab="", ylab="ZScore", main=stat, pch=16, cex=2, col = "blue", xaxt = "n")
  abline(h = 0, lwd = 1, col = "green") ;
  for (i in 1:length(x1)){
    segments(1, x1[i], 2, x2[i], col = "grey", lwd = 1)
  }
  segments(1, mean(x1), 2, mean(x2), col = "black", lwd = 2)
  points(1,mean(x1), pch=16, cex=2, col = "blue")
  points(2,mean(x2), pch=16, cex=2, col = "red")
  arrows(x0=1, y0=mean(x1) - sd(x1)/sqrt(length(x1)), x1=1, y1=mean(x1) + sd(x1)/sqrt(length(x1)), code=3, angle=90, length=0.1, col = "blue")
  arrows(x0=2, y0=mean(x2) - sd(x2)/sqrt(length(x2)), x1=2, y1=mean(x2) + sd(x2)/sqrt(length(x2)), code=3, angle=90, length=0.1, col = "red")
  axis(1, at = c(1, 2), labels = labels)
}

strClean = function(y){
  # to clean brackets and braces from some string
  y = gsub("\"", "", y)
  y = gsub("}", "", y)
  y = gsub("[{]", "", y)
  y = gsub("[[]", "", y)
  y = gsub("[]]", "", y)
  y = gsub('"', "", y)
  return(y)
}

euclid = function(x1,x2,y1,y2){
  # get euclidian / pythagorean distance between two points (x1,y1) vs (x2,y2)
  z = (((x2 - x1)^2) + ((y2 - y1)^2))^0.5
  return(z)
}

findAngle = function(x2,y2,x1 = 0, y1 = 0){
  # find angle (degrees) between two points (x1,y1) vs (x2,y2). If x1 and y2 not specified, find angle from origin (0,0)
  # 90 degrees is north, east is 0, south is 270, south-west is 225 degrees. Wraps at 360 = 0 degrees (east)
  angle = atan2(y2-y1,x2-x1) * 180/pi
  angle[angle < 0] = angle[angle < 0] + 360
  angle[angle > 360] = angle[angle > 360] - 360
  return(angle)
}

calcZT = function(raw_score,ref_mean = NA,ref_sd = NA){
  # To calculate the zscore and percentiles of a set of scores (given some reference mean and sd, else, take sample statistics)
  # use case 1 (with reference) : data = calcZT(rnorm(100, mean = 50, sd = 15), ref_mean = 50, ref_sd = 15)
  # use case 2 (no reference) : data = calcZT(rnorm(100, mean = 50, sd = 15))
  if (is.na(ref_mean)){ref_mean = mean(raw_score); ref_sd = sd(raw_score)}
  z_score = (raw_score - ref_mean) / ref_sd
  percentile = pnorm(z_score) * 100
  data = data.frame(raw_score,z_score, percentile)
  return(data)
}

makeCorMat = function(data){
  # make a correlation matrix. Assumes first column is excluded and all other columns indicate some variable
  numFeatures = length(names(data)) - 1
  corMat = matrix(NA,ncol = numFeatures, nrow = numFeatures)
  colnames(corMat) = names(data)[1:13 + 1]
  rownames(corMat) = names(data)[1:13 + 1]
  for (i in 1:numFeatures){
    for (j in 1:numFeatures){
      corMat[i,j] = cor(data[,i+1],data[,j+1])
    }
  }
  return(corMat)
}

corMap = function(corMat, patternMap = c("a","b","c","d","e")){
  # plot the output of makeCorMat, e.g.:
  #data = data.frame(index = 1:100) # # make correlation matrix
  #for (i in 2:14){
  #  data[,i] = rnorm(length(data$index),0,1)
  #}
  #names(data) = c("index","a1","a2","b1","b2","b3","c1","c2","d1","d2","d3","e1","e2","e3")
  #corMat = makeCorMat(data)
  #corMap(corMat)
  rowNames = colnames(corMat)
  numFeatures = length(rowNames)
  par(las=2)
  par(mar=c(1,1,1,1)) # adjust as needed
  x = seq(-1,1,0.01)
  colfunc = colorRampPalette(c("red","white","royalblue"))
  colHex = colfunc(length(x))
  plot(-100,-100,xlim = c(-2,numFeatures) , ylim = c(-2,numFeatures), xlab = "", ylab = "", xaxt="n", yaxt="n")
  for (i in 1:numFeatures){
    for (j in 1:numFeatures){
      colIdx = ((1+round(corMat[i,j],2)) / 0.01)+1    
      rect(i-0.5,j-0.5,i+0.5,j+0.5,col = colHex[colIdx])
    }
    if (length(grep(rowNames[i], pattern = patternMap[1]))>0){points(i,-0.2, col = 'black', pch = 19); points(-0.2,i, col = 'black', pch = 19);     text(i,-1,rowNames[i], col = 'black', srt = 90) ; text(-1,i,rowNames[i], col = 'black') }
    if (length(grep(rowNames[i], pattern = patternMap[2]))>0){points(i,-0.2, col = 'orange', pch = 19); points(-0.2,i, col = 'orange', pch = 19);     text(i,-1,rowNames[i], col = 'orange', srt = 90); text(-1,i,rowNames[i], col = 'orange')  }
    if (length(grep(rowNames[i], pattern = patternMap[3]))>0){points(i,-0.2, col = 'purple', pch = 19); points(-0.2,i, col = 'purple', pch = 19);     text(i,-1,rowNames[i], col = 'purple', srt = 90); text(-1,i,rowNames[i], col = 'purple')  }  
    if (length(grep(rowNames[i], pattern = patternMap[4]))>0){points(i,-0.2, col = 'cyan', pch = 19); points(-0.2,i, col = 'cyan', pch = 19);     text(i,-1,rowNames[i], col = 'cyan', srt = 90); text(-1,i,rowNames[i], col = 'cyan')  }  
    if (length(grep(rowNames[i], pattern = patternMap[5]))>0){points(i,-0.2, col = 'red', pch = 19); points(-0.2,i, col = 'red', pch = 19);     text(i,-1,rowNames[i], col = 'red', srt = 90); text(-1,i,rowNames[i], col = 'red')  }  
 }
}

############ plot examples
#dev.new() # open a new window for plot
#par(mfrow=c(2,1)) # panels
#par(mar=c(4,7,3,1)) # set margins
#set.seed(15)
#x = 1:100; y = dnorm(x, mean = 50, sd = 10) # data
#plot(-10,10,xlim=c(min(x),max(x)), ylim=c(min(y)-0.02,max(y)+0.02), ylab="", cex.axis = 0.5,xlab ="", xaxt = "n", main = "Title", )
#for(sim in 1:5){lines(x,y+rnorm(10,mean = 0, sd = 0.005), col = colors()[sample(length(colors()))[1]])} # lines
#segments(x,0,x,y,lwd = 1, col = "grey") # faux bar plot
#abline(v = 50, lwd = 3) ; abline(h = 00, lwd = 1, col = "grey") # vertical / horizontal lines
#axis(1, at=x, labels=paste0('SD = ',(x-50)/10),las=3,cex.axis = 0.5)
#pairedPlot(x1 = rnorm(30,-1,3), x2 = rnorm(30,1,3.2), labels = c("x1","x2"))

# to plot and correlation matrix (corMat), and export to a jpeg
#peg("./output.jpeg", width = 8, height = 8, units = 'in', res = 300)
#par(las=2); par(mar=c(10,10,1,1))
#colfunc = colorRampPalette(c("red","white","royalblue"))
#x = seq(-1,1,0.01); colHex = colfunc(length(x))
#corMat = matrix(runif(100, min = -1, max = 1), ncol = 10); rownames(corMat) = paste0('x',1:10); colnames(corMat) = paste0('x',1:10) #data
#plot(-100,-100,xlim = c(1,10) , ylim = c(1,10), xlab = "", ylab = "", xaxt="n", yaxt="n")
#for (i in 1:10){
#  for (j in 1:10){
#    colIdx = ((1+round(corMat[i,j],2)) / 0.01)+1    
#    rect(i-0.5,j-0.5,i+0.5,j+0.5,col = colHex[colIdx])
#    text(i,j,labels = round(corMat[i,j],2), cex = 1.0, col = "black")
#  }
#}
#axis(side=1, at=1:10, labels = rownames(corMat) , cex.axis = 1, font=2)
#axis(side=2, at=1:10, labels = rownames(corMat) , cex.axis = 1, font=2)
#dev.off()


############ other how to's:

####how to connect R to a postgresql:
#library(DBI)
#con = dbConnect(RPostgres::Postgres(), dbname = 'a', host = 'b', port = 5432, user = 'user', password = 'pass')
#query = "SELECT * FROM INFORMATION_SCHEMA.TABLES"; #tables = dbGetQuery(con, query)
#query = "SELECT * FROM db.table WHERE somecolumn like 'pattern%'"; #d = dbGetQuery(con, query)

####make a virtual SQL connection, some basic functionality from R
#install.packages("RSQLite")
#install.packages("DBI")
#library(DBI)

# Prep some data
#data = iris
#colnames(data) = c("SL","SW","PL","PW","Species") # give column names that sql works easily with
#speciesID = data.frame(sID = 1:3, Species = unique(data$Species)) # a second table to give an id number to the species

# make a sql server connection
#con = dbConnect(RSQLite::SQLite(), dbname = ":memory:")
#dbWriteTable(con, "data", data)
#dbWriteTable(con, "speciesID", speciesID)
#dbListTables(con) # just to check that we have 2 tables
#rm(list = c("data", "speciesID")) # clear from memory the table

# Basic selection
#dbGetQuery(con, "SELECT * FROM data") # select all columns
#dbGetQuery(con, "SELECT SL,SW FROM data WHERE Species = 'virginica' ") # select some columns based on some other column value
#dbGetQuery(con, "SELECT SL,SW FROM data WHERE Species LIKE 'V%' ") # same as above, but filter based on pattern

# AND / OR
#dbGetQuery(con, "SELECT * FROM data WHERE PW > 0.5 OR  PL > 5.0")
#dbGetQuery(con, "SELECT * FROM data WHERE PW > 0.5 AND  PL > 5.0")

# SUM / minmax / count / avg
#dbGetQuery(con, "SELECT COUNT(SW) FROM data WHERE PW > 0.5 OR  PL > 5.0")
#dbGetQuery(con, "SELECT COUNT(SW) FROM data WHERE PW > 0.5 AND  PL > 5.0")
#dbGetQuery(con, "SELECT MIN(SW),AVG(SW),MAX(SW) FROM data WHERE PW > 0.5 AND  PL > 5.0")
#dbGetQuery(con, "SELECT AVG(SW) FROM data WHERE PW > 0.5 AND  PL > 5.0")

# joining 2 tables based on some common attribute (e.g. data and speciesID both have a "Species" column)
#dbGetQuery(con, "SELECT * FROM data INNER JOIN speciesID ON data.Species=speciesID.Species")
#dbGetQuery(con, "SELECT data.SL,speciesID.sID FROM data INNER JOIN speciesID ON data.Species=speciesID.Species")

# End
#dbDisconnect(con)

####join data.frames by some ID column
#d = merge(d1,d2,by="id", all = TRUE)

####read json files
#library(jsonlite)
#read_json(file)

####dealing with timestamps
#timestamp1 = as.POSIXct(1678192830, origin = '1970-01-01')
#timestamp2 = as.POSIXct(1678198240, origin = '1970-01-01')
#diff_in_mins = as.numeric(difftime(timestamp2,timestamp1,units = "mins"))

####how to use data.frames
#data = data.frame(userID = c('s1','s2','s3'), score = c(100,95,82)) ## make a data.frame
#data$score[data$userID == "s1"] # get a value of one column based on another
#data[data$userID == "s2",] # return the whole row
#data$score2 = NA # make a new empty column
#data$score2[data$userID == "s3"] = 98 # update a data point
#data = data[order(data$score),] #ordering a data.frame
