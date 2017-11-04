import pyjsdl as pygame
import random

# custom functions
red = (255,0,0)
green = (0,255,0)
white = (255,255,255)
black = (0,0,0)

pygame.init()
resX = 600
resY = 600
screen = pygame.display.set_mode((resX, resY))
pygame.display.set_caption('SpaDect')
font = pygame.font.Font(None, 24)

screen.fill(black)
pygame.display.flip() 

posx = int(random.uniform(100,500))
posy = int(random.uniform(100,500))
clickPos = [-1,-1]

def run():
    global clickPos

    posx = int(random.uniform(100,500))
    posy = int(random.uniform(100,500))

    screen.fill(black)
    for event in pygame.event.get():
        if (event.type == pygame.MOUSEBUTTONUP):
            clickPos = pygame.mouse.get_pos()
            pygame.draw.circle(screen, white, [posx,posy], 15, 0)

    mousePos = pygame.mouse.get_pos()
    string = 'X:'+ str(mousePos[0]) + '   Y:'+ str(mousePos[1])
    text = font.render(string, 1, white)
    screen.blit(text, [250,50])

    string = 'Clicked X: ' + str(clickPos[0]) + '  Clicked Y: ' + str(clickPos[1])
    text = font.render(string, 1, green)
    screen.blit(text, [200,500])
	
    pygame.display.flip()
                   
pygame.display.setup(run)
