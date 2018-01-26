ui <- fluidPage(
  
  titlePanel("Sample Questionnaire"),
  
  # Sidebar
  sidebarLayout(

    # Sidebar panel for inputs ----
    sidebarPanel(
        helpText('Written by', a("Syaheed Jabar", href="https://syaheed.tech")), 
        textInput("UserID", "ID:", "UserID") ,
        uiOutput("qNum"),
        tableOutput('table')
    ),


    # Main panel
    mainPanel(
      h3(textOutput('Head')),
      h4(textOutput('Question')),
      h1(""), # insert blank

      h1(""), # insert blank
      uiOutput("UserChoice"),
      actionButton("save", "Save"),
      h1(""), # insert blank
      imageOutput("Image", height = 100)

    )
  )
)



# Server logic

server <- function(input, output) {

	writeRow <- function(data,filename){
		ansRow = as.matrix(t(data))
		write.table(ansRow, file = filename, col.names = FALSE, row.names=FALSE, sep = ',', append = TRUE)
	}

	randString <- function(n = 1) {
		  a <- do.call(paste0, replicate(5, sample(LETTERS, n, TRUE), FALSE))
			paste0(a, sprintf("%04d", sample(9999, n, TRUE)), sample(LETTERS, n, TRUE))
	}

	qlist = list.files(pattern = '.csv')
	qlist = sample(qlist, 1) # randomly pick an availible .csv

  if(exists("qtable") == FALSE){
    qtable = read.csv(qlist, header = TRUE)
    num_q = length(qtable$Num)
    start_time = format(Sys.time(), "%d%b%y_%X");

	filename = paste0(getwd(), '/UserResp/', randString(), '_', start_time, '_', qlist)
	data = c('UserID','Num','Time','Question','Answer')
	writeRow(data,filename)
}

  output$UserID <- renderText({ input$UserID })
  
  output$qNum <- renderUI({
        radioButtons("qNum", "Questions", choices = 1:num_q, inline=T)
    })
    
  output$Head = renderText({paste('Question',input$qNum,':')})
  output$Question = renderText({paste(qtable$Question[as.numeric(input$qNum)])})

  output$UserChoice <- renderUI({
        qNum = as.numeric(input$qNum);
        numChoices = qtable$NumChoices[qNum];
        default_choice = as.character(qtable$UserChoice[qNum]);
        choice_list = as.character(qtable[qNum,4]);
        for(i in 2:numChoices){
             choice_list = rbind(choice_list,as.character(qtable[qNum,4-1+i]));
        };

        output$Image = renderImage({list(src = as.character(qtable$Image[qNum]))});
        radioButtons("UserChoice", "Choose one:", choices = choice_list, selected = default_choice, inline=F)
  })


  observeEvent(input$save, {
				UserID = as.character(input$UserID);
				qNum = as.numeric(input$qNum);
				Answer = as.character(input$UserChoice);
				time = format(Sys.time(), "%d%b%y_%X");
				data = c(UserID, as.character(qNum) , time, as.character(qtable$Question[qNum]), Answer)
				writeRow(data,filename)

				responses = read.csv(filename, header = TRUE)
				indexes = tapply(seq_along(responses$Num), responses$Num, max)
				responses = subset(responses, select = -c(UserID,Time))
				output$table = renderTable({responses[indexes,]},include.rownames=FALSE)
				})

}
