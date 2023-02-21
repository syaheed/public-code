rowsplit = function(x,column = 0, sp= "_"){
# splits rows of strings into a matrix based on a seperator (sp), and either returns the whole matrix (column = 0), or a particular column
  temp = do.call(rbind,strsplit(x,sp))
  if(column == 0){return(temp)}
  if(column > 0){return(temp[,column])}
}
