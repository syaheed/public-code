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
