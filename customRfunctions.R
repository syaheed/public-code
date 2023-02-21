# This is just a function list / help page for things that I find myself using quite a bit.

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

############ plot examples
#dev.new() # open a new window for plot
#par(mfrow=c(2,1)) # panels
#par(mar=c(4,7,3,1)) # set margins

#set.seed(15)
#x = 1:100; y = dnorm(x, mean = 50, sd = 10)
#plot(-10,10,xlim=c(min(x),max(x)), ylim=c(min(y)-0.02,max(y)+0.02), ylab="", cex.axis = 0.5,xlab ="", xaxt = "n", main = "Title", )
#for(sim in 1:5){lines(x,y+rnorm(10,mean = 0, sd = 0.005), col = colors()[sample(length(colors()))[1]])} # lines
#segments(x,0,x,y,lwd = 1, col = "grey") # faux bar plot
#abline(v = 50, lwd = 3) ; abline(h = 00, lwd = 1, col = "grey") # vertical / horizontal lines
#axis(1, at=x, labels=paste0('SD = ',(x-50)/10),las=3,cex.axis = 0.5)

############ other how to's:

#how to connect R to a postgresql:
#library(DBI)
#con = dbConnect(RPostgres::Postgres(), dbname = 'a', host = 'b', port = 5432, user = 'user', password = 'pass')
#query = "SELECT * FROM INFORMATION_SCHEMA.TABLES"; #tables = dbGetQuery(con, query)
#query = "SELECT * FROM db.table WHERE somecolumn like 'pattern%'"; #d = dbGetQuery(con, query)

#join data.frames by some ID column
#d = merge(d1,d2,by="id", all = TRUE)

#read json files
#library(jsonlite)
#read_json(file)

#dealing with timestamps
#timestamp1 = as.POSIXct(1678192830, origin = '1970-01-01')
#timestamp2 = as.POSIXct(1678198240, origin = '1970-01-01')
#difftime(timestamp2,timestamp1,units = "mins")

#ordering a data.frame
#d = d[order(d$timestamp),]
