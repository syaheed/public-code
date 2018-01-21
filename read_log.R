read_log <- function(i,file_list){

  file = readLines(file_list[i])
  
  trial_index = grep('Trials:', file, useBytes = TRUE)
  Trial = as.numeric(unlist(read.table(text = file[trial_index], sep = "", colClasses = "character")[2]))
  num_trials = length(Trial)
  
  subj_index = grep('Subject:', file, useBytes = TRUE)[1]
  subject = as.numeric(read.table(text = file[subj_index], sep = "", colClasses = "character")[2])
  Subject = rep(subject,num_trials)
  
  final_amt_index = grep('AmtWon:', file, useBytes = TRUE)[1]
  amtwon = as.numeric(read.table(text = file[final_amt_index], sep = "", colClasses = "character")[2])
  AmtWon = rep(amtwon,num_trials)
  
  session_index = grep('Session:', file, useBytes = TRUE)[1]
  session = as.numeric(read.table(text = file[session_index], sep = "", colClasses = "character")[2])
  Session = rep(session,num_trials)
  
  date_index = grep('Date:', file, useBytes = TRUE)[1]
  date = read.table(text = file[date_index], sep = "", colClasses = "character")[2]
  Date = rep(date()[1],num_trials)
  
  procedure_index = grep('Procedure:', file, useBytes = TRUE)
  Procedure = unlist(read.table(text = file[procedure_index], sep = "", colClasses = "character")[2])
  
  amount_index = grep('Amount:', file, useBytes = TRUE)
  Amount = as.numeric(unlist(read.table(text = file[amount_index], sep = "", colClasses = "character")[2]))
  
  probability_index = grep('Probability:', file, useBytes = TRUE)
  Probability = as.numeric(unlist(read.table(text = file[probability_index], sep = "", colClasses = "character")[2]))
  
  rt_index = grep('RT:', file, useBytes = TRUE)
  RT = as.numeric(unlist(read.table(text = file[rt_index], sep = "", colClasses = "character")[2]))
  
  choice_index = grep('Choice:', file, useBytes = TRUE)
  Choice = as.numeric(unlist(read.table(text = file[choice_index], sep = "", colClasses = "character")[2]))
  
  tapspeed_index = grep('TapSpeed:', file, useBytes = TRUE)
  TapSpeed = as.numeric(unlist(read.table(text = file[tapspeed_index], sep = "", colClasses = "character")[2]))
  
  completed_index = grep('Completed:', file, useBytes = TRUE)
  Completed = as.numeric(unlist(read.table(text = file[completed_index], sep = "", colClasses = "character")[2]))
  
  winnings_index = grep('Winnings:', file, useBytes = TRUE)
  Winnings = as.numeric(unlist(read.table(text = file[winnings_index], sep = "", colClasses = "character")[2]))
  
  data = data.frame(Subject,Session,Date,Trial,Procedure,Amount,Probability,RT,Choice,TapSpeed,Completed,Winnings,AmtWon)
  rownames(data) = c()
  return(data) 
}






