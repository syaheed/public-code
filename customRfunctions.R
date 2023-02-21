# how to use:
#library(devtools)
#source_url("https://raw.githubusercontent.com/syaheed/public-code/master/customRfunctions.R")

rowsplit = function(x,column = 0, sp= "_"){
# splits rows of strings into a matrix based on a seperator (sp), and either returns the whole matrix (column = 0), or a particular column
  temp = do.call(rbind,strsplit(x,sp))
  if(column == 0){return(temp)}
  if(column > 0){return(temp[,column])}
}

# how to connect R to a postgresql:
#library(DBI)
#con = dbConnect(RPostgres::Postgres(), dbname = 'a', host = 'b', port = 5432, user = 'user', password = 'pass')
#query = "SELECT * FROM INFORMATION_SCHEMA.TABLES"
#d = dbGetQuery(con, query)
