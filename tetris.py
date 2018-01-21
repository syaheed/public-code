# tetris
# python C:\Users\Syaheed\Dropbox\Waterloo\tetris\tetris.py
# python2 /home/syaheed/Dropbox/Waterloo/tetris/tetris.py


# import libraries
import pygame
import sys
import numpy as np
import random
import os 

path = os.path.dirname(os.path.realpath(__file__))
music_names = [fn for fn in os.listdir(path)
              if any(fn.startswith (ext) for ext in ['music'])]

pygame.init()
myfont = pygame.font.SysFont("monospace", 24, True)

rewardTone = pygame.mixer.Sound(path + '/' + 'reward.wav')

end_file = (path + '/' + 'GameOver.mp3')
endTone = pygame.mixer.Sound(end_file)

pygame.key.set_repeat (50, 50)

# custom functions
red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)
darkBlue = (0,0,128)
white = (255,255,255)
black = (0,0,0)
pink = (255,200,200)
gray = (100,100,100)

# initialise
pygame.init()
res = (640,640)
screen = pygame.display.set_mode(res)
screen.fill(black)
pygame.display.set_caption('Tetris')
pygame.display.flip()

# background
back_x = int(res[0]/2.5)
back_off = int((res[0] - back_x)/3)

# Squares
num_col = 10
sq_size = back_x/num_col
num_row = int(res[1]/ sq_size)
back_y = sq_size*num_row

empty_grid = np.zeros((num_row,num_col)).astype(int)
set_grid = empty_grid
tgt_grid = empty_grid

x = back_off + sq_size*np.array(range(0,num_col))
pos_grid_x = np.tile(x, (num_row, 1))

y = sq_size*np.array(range(0,num_row))
pos_grid_y = np.tile(y, (num_col, 1))
pos_grid_y = np.transpose(pos_grid_y)

col_list = [gray,white,red,blue,green,gray]

start_x = 4
start_y = 0


### Targets ######

blank = np.array([[start_x], [start_y] ])

t_line_1 = np.array([[start_x,start_x,start_x,start_x], [start_y-1,start_y-2,start_y-3,start_y-4] ])
t_line_2 = np.array([[start_x-1,start_x,start_x+1,start_x+2], [start_y-2,start_y-2,start_y-2,start_y-2] ])

t_square = np.array([[start_x,start_x,start_x+1,start_x+1], [start_y-2,start_y-1,start_y-2,start_y-1] ])

t_L1_1 = np.array([[start_x,start_x,start_x,start_x+1], [start_y-3,start_y-2,start_y-1,start_y-1] ])
t_L1_2 = np.array([[start_x-1,start_x-1,start_x,start_x+1], [start_y-2,start_y-1,start_y-2,start_y-2] ])
t_L1_3 = np.array([[start_x,start_x+1,start_x+1,start_x+1], [start_y-3,start_y-3,start_y-2,start_y-1] ])
t_L1_4 = np.array([[start_x-1,start_x,start_x+1,start_x+1], [start_y-1,start_y-1,start_y-1,start_y-2] ])

t_L2_1 = np.array([[start_x+1,start_x+1,start_x+1,start_x], [start_y-3,start_y-2,start_y-1,start_y-1] ])
t_L2_2 = np.array([[start_x-1,start_x-1,start_x,start_x+1], [start_y-2,start_y-1,start_y-1,start_y-1] ])
t_L2_3 = np.array([[start_x,start_x,start_x,start_x+1], [start_y-1,start_y-2,start_y-3,start_y-3] ])
t_L2_4 = np.array([[start_x-1,start_x,start_x+1,start_x+1], [start_y-2,start_y-2,start_y-2,start_y-1] ])

t_T_1 = np.array([[start_x-1,start_x,start_x,start_x+1], [start_y-1,start_y-1,start_y-2,start_y-1] ])
t_T_2 = np.array([[start_x,start_x,start_x,start_x+1], [start_y-3,start_y-2,start_y-1,start_y-2] ])
t_T_3 = np.array([[start_x-1,start_x,start_x,start_x+1], [start_y-2,start_y-2,start_y-1,start_y-2] ])
t_T_4 = np.array([[start_x-1,start_x,start_x,start_x], [start_y-2,start_y-3,start_y-2,start_y-1] ])

t_S1_1 = np.array([[start_x-1,start_x,start_x,start_x+1], [start_y-1,start_y-1,start_y-2,start_y-2] ])
t_S1_2 = np.array([[start_x+1,start_x+1,start_x,start_x], [start_y-2,start_y-1,start_y-2,start_y-3] ])

t_S2_1 = np.array([[start_x-1,start_x,start_x,start_x+1], [start_y-2,start_y-2,start_y-1,start_y-1] ])
t_S2_2 = np.array([[start_x,start_x,start_x+1,start_x+1], [start_y-2,start_y-1,start_y-2,start_y-3] ])

#### Custom functions ####

def drawBack():
    pygame.draw.rect(screen,gray,(back_off,0,num_col*sq_size,back_y))

def drawSet(grid):
    itemindex = np.where(grid>0)
    x = itemindex[0]
    y = itemindex[1]
    num_items = len(x)
    
    for i in range(num_items):
        xi = x[i]
        yi = y[i]
        if yi >= 0:
            col = grid[xi,yi]
            pygame.draw.rect(screen,col_list[col],(pos_grid_x[xi,yi],pos_grid_y[xi,yi],sq_size,sq_size),0)
            pygame.draw.rect(screen,black,(pos_grid_x[xi,yi],pos_grid_y[xi,yi],sq_size,sq_size),1)

def drawTgt(tgt,col,grid):
    if (grid[1,5]==0):
        tgt_grid = empty_grid
        num_sq = len(tgt[1])
        x = tgt[0]
        y = tgt[1]
        for i in range(num_sq):
            if (y[i] >= 0):
                pygame.draw.rect(screen,col_list[col],(pos_grid_x[y[i],x[i]],pos_grid_y[y[i],x[i]],sq_size,sq_size),0)
                pygame.draw.rect(screen,black,(pos_grid_x[y[i],x[i]],pos_grid_y[y[i],x[i]],sq_size,sq_size),1)  
                
def drawSide(tgt):
    num_sq = len(tgt[1])
    x = tgt[0]
    y = tgt[1] 
    for i in range(num_sq):
        pygame.draw.rect(screen,gray,(pos_grid_x[y[i],x[i]] + 200,pos_grid_y[y[i],x[i]]-100,sq_size,sq_size),0)   
        pygame.draw.rect(screen,black,(pos_grid_x[y[i],x[i]] + 200,pos_grid_y[y[i],x[i]]-100,sq_size,sq_size),1)   

def oneDown(tgt,grid):
    bot = 0
    down = 0
    x = tgt[0]
    y = tgt[1]
    num_sq = len(x)
    
    maxy = max(tgt[1])
    if (maxy ==  num_row-1):
        bot = 1
    else:    
        for i in range(num_sq):
            xi = x[i]
            yi = y[i]
            if yi >= 0:
                if grid[yi+1,xi] > 0:
                    bot = 1
    if bot == 0:
        y = y+1
        down = 1
    return(np.array([x,y]),bot,down)


def checkLeft(tgt,grid):
    go = -1
    x = tgt[0]
    y = tgt[1]
    num_sq = len(x)
    
    minx = min(tgt[0])
    if (minx ==  0):
        go = 0
    else:    
        for i in range(num_sq):
            xi = x[i]
            yi = y[i]
            if grid[yi,xi-1] > 0:
                go = 0
    return(go)
    
    
def checkRight(tgt,grid):
    go = 1
    x = tgt[0]
    y = tgt[1]
    num_sq = len(x)
    
    maxx = max(tgt[0])
    if (maxx ==  num_col-1):
        go = 0
    if go == 1:    
        for i in range(num_sq):
            xi = x[i]
            yi = y[i]
            if grid[yi,xi+1] > 0:
                go = 0
    return(go)
          
def tgt2set(tgt,tc,grid):
    num_sq = len(tgt[1])
    x = tgt[0]
    y = tgt[1]
    for i in range(num_sq):
        if y[i] >= 0:
            grid[y[i],x[i]] = tc  
    return(grid)

 
def delCom(grid):
    phy_grid = np.zeros((num_row,num_col)).astype(int)
    phy_grid[grid>0] = 1
    index = np.where(np.sum(phy_grid, axis=1) == num_col)[0]
    grid_temp = grid
    grid_temp[index,:] = 5
    grid = np.delete(grid, index, 0) # delete row index
    r = 0
    removed = len(index)
    repl = np.zeros((removed,num_col)).astype(int)
    grid = np.append(repl,grid,0)
    
    if removed > 0:
        r = removed
        rewardTone.set_volume(0.2*removed)
        rewardTone.play()
        pygame.time.delay(400)
     
    return(grid,r,grid_temp)

def drawAll():
    screen.fill(black)
    drawBack()
    drawTgt(target,t_col,set_grid)
    drawSet(set_grid)
    drawSide(next_target)
    screen.blit(score, (400, 100))
    screen.blit(lineClear, (400, 150))
    pygame.display.flip()
 
def rotTgtc(tgt):
    x = tgt[0]-shift
    y = tgt[1]-fall
    otgt = np.array([x,y])
    ntgt = otgt
    
    if np.sum(np.absolute(otgt - t_line_1))==0:
        ntgt = t_line_2
    elif np.sum(np.absolute(otgt - t_line_2))==0:
        ntgt = t_line_1
    elif np.sum(np.absolute(otgt - t_square))==0:
        ntgt = t_square
    elif np.sum(np.absolute(otgt - t_L1_1))==0:
        ntgt = t_L1_2
    elif np.sum(np.absolute(otgt - t_L1_2))==0:
        ntgt = t_L1_3
    elif np.sum(np.absolute(otgt - t_L1_3))==0:
        ntgt = t_L1_4
    elif np.sum(np.absolute(otgt - t_L1_4))==0:
        ntgt = t_L1_1
    elif np.sum(np.absolute(otgt - t_L2_1))==0:
        ntgt = t_L2_2
    elif np.sum(np.absolute(otgt - t_L2_2))==0:
        ntgt = t_L2_3
    elif np.sum(np.absolute(otgt - t_L2_3))==0:
        ntgt = t_L2_4
    elif np.sum(np.absolute(otgt - t_L2_4))==0:
        ntgt = t_L2_1            
    elif np.sum(np.absolute(otgt - t_S1_1))==0:
        ntgt = t_S1_2
    elif np.sum(np.absolute(otgt - t_S1_2))==0:
        ntgt = t_S1_1
    elif np.sum(np.absolute(otgt - t_S2_1))==0:
        ntgt = t_S2_2
    elif np.sum(np.absolute(otgt - t_S2_2))==0:
        ntgt = t_S2_1 
    elif np.sum(np.absolute(otgt - t_T_1))==0:
        ntgt = t_T_2
    elif np.sum(np.absolute(otgt - t_T_2))==0:
        ntgt = t_T_3
    elif np.sum(np.absolute(otgt - t_T_3))==0:
        ntgt = t_T_4
    elif np.sum(np.absolute(otgt - t_T_4))==0:
        ntgt = t_T_1
           
    ftgt = np.array([ntgt[0]+shift,ntgt[1]+fall])
    x = ftgt[0]
    y = ftgt[1]
    num_sq = len(x)
    change=1
    if min(x) < 0:
        change = 0
    if max(x) >= num_col:
        change = 0
    for i in range(num_sq):
        if x[i] < num_col-2:
            if set_grid[y[i],x[i]] > 0:  
                change = 0
                break
    if change == 1:              
        return(ftgt)
    else:
        return(tgt)

def rotTgta(tgt):
    x = tgt[0]-shift
    y = tgt[1]-fall
    otgt = np.array([x,y])
    ntgt = otgt
    
    if np.sum(np.absolute(otgt - t_line_1))==0:
        ntgt = t_line_2
    elif np.sum(np.absolute(otgt - t_line_2))==0:
        ntgt = t_line_1
    elif np.sum(np.absolute(otgt - t_square))==0:
        ntgt = t_square
    elif np.sum(np.absolute(otgt - t_L1_1))==0:
        ntgt = t_L1_4
    elif np.sum(np.absolute(otgt - t_L1_2))==0:
        ntgt = t_L1_1
    elif np.sum(np.absolute(otgt - t_L1_3))==0:
        ntgt = t_L1_2
    elif np.sum(np.absolute(otgt - t_L1_4))==0:
        ntgt = t_L1_3    
    elif np.sum(np.absolute(otgt - t_L2_1))==0:
        ntgt = t_L2_4
    elif np.sum(np.absolute(otgt - t_L2_2))==0:
        ntgt = t_L2_1
    elif np.sum(np.absolute(otgt - t_L2_3))==0:
        ntgt = t_L2_2
    elif np.sum(np.absolute(otgt - t_L2_4))==0:
        ntgt = t_L2_3     
    elif np.sum(np.absolute(otgt - t_S1_1))==0:
        ntgt = t_S1_2
    elif np.sum(np.absolute(otgt - t_S1_2))==0:
        ntgt = t_S1_1
    elif np.sum(np.absolute(otgt - t_S2_1))==0:
        ntgt = t_S2_2
    elif np.sum(np.absolute(otgt - t_S2_2))==0:
        ntgt = t_S2_1 
    elif np.sum(np.absolute(otgt - t_T_1))==0:
        ntgt = t_T_4
    elif np.sum(np.absolute(otgt - t_T_2))==0:
        ntgt = t_T_1
    elif np.sum(np.absolute(otgt - t_T_3))==0:
        ntgt = t_T_2
    elif np.sum(np.absolute(otgt - t_T_4))==0:
        ntgt = t_T_3
               
    ftgt = np.array([ntgt[0]+shift,ntgt[1]+fall])
    x = ftgt[0]
    y = ftgt[1]
    num_sq = len(x)
    change = 1
    if min(x) < 0:
        change = 0
    if max(x) >= num_col:
        change = 0
    for i in range(num_sq):
        if x[i] < num_col-2:
            if set_grid[y[i],x[i]] > 0:  
                change = 0
                break
    if change == 1:              
        return(ftgt)
    else:
        return(tgt)
    
    
#### Main Loop ####

retry = 1

while retry == 1: 
    n = random.choice(range(len(music_names)))
    music = music_names[n]
    pygame.mixer.music.load(path + '/' + music)
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(-1) 
    
    set_grid = np.zeros((num_row,num_col)).astype(int)
    tgt_grid = np.zeros((num_row,num_col)).astype(int)
    target = blank
    
    screen.fill(black)
    drawBack()
    pygame.display.flip()
    pygame.time.delay(400)
    
    t_points = 0
    trial = 0
    lose = 0
    lines = 0
    shift = 0
    fall = 0
    score = myfont.render('Score: '+str(t_points), 1, (255,255,255))
    lineClear = myfont.render('Lines: '+str(lines), 1, (255,255,255))
    
    while (lose == 0):
        trial = trial +1
        t_col = int(random.uniform(1,5))
        if trial == 1:
            orig_target = random.choice([t_square,t_line_1,t_L1_1,t_L2_1,t_S1_1,t_S2_1,t_T_1])
        else:
            orig_target = next_target
        target = orig_target
        next_target = random.choice([t_square, t_line_1, t_line_1, t_L1_1, t_L2_1, t_S1_1, t_S2_1, t_T_1])
        
        rot = random.choice([1,2,3])
        for i in range(rot):
            next_target=rotTgta(next_target)
        
        bot = 0
        point = 0
        go = 0
        shift = 0
        fall = 0
        
        while (bot == 0):
            s = pygame.time.get_ticks()
            
            while (pygame.time.get_ticks()-s) < (200):
                events = pygame.event.get()
                for event in events:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_LEFT:
                           go = checkLeft(target,set_grid)
                           if go == -1:
                               x=target[0]
                               y=target[1]
                               target = np.array([x-1,y])
                               shift = shift + go
                               drawAll()
                        if event.key == pygame.K_RIGHT:
                           go = checkRight(target,set_grid)
                           if go == 1:
                               x=target[0]
                               y=target[1]
                               target = np.array([x+1,y])
                               shift = shift + go
                               drawAll()
                        if event.key == pygame.K_x:
                            pygame.key.set_repeat (100, 100)    
                            target = rotTgta(target)
                            drawAll()
                            pygame.key.set_repeat (50, 50)
                        if event.key == pygame.K_z:
                            target = rotTgtc(target)
                            drawAll()
                            pygame.key.set_repeat (50, 50)
                        if event.key == pygame.K_q:
                               pygame.quit()
                               sys.exit() 
                        if event.key == pygame.K_DOWN:
                            t = oneDown(target,set_grid)
                            target = t[0]
                            bot = t[1]
                            if t[2] == 1:
                                fall = fall + 1
                            drawAll()
                        
            t = oneDown(target,set_grid)
            target = t[0]
            bot = t[1]
            if t[2] == 1:
                fall = fall + 1           
            drawAll()
                
        set_grid = tgt2set(target,t_col,set_grid)
        
        rem = delCom(set_grid)
        set_grid = rem[2]
        drawAll()
        set_grid = rem[0]
        lines = lines + rem[1]
        point = (rem[1]*10)**2
        t_points = t_points + point
        score = myfont.render('Score: '+str(t_points), 1, (255,255,255))
        lineClear = myfont.render('Lines: '+str(lines), 1, (255,255,255))
    
        if set_grid[0,start_x] > 0:
            pygame.mixer.music.load(path + '/' + 'GameOver.mp3')
            pygame.mixer.music.set_volume(0.2)
            pygame.mixer.music.play() 
            drawAll()

            pygame.time.delay(1000)
            set_grid[set_grid>0] = 5
            drawAll()
            lose = 1
            retry = 0
            pygame.time.delay(4500)
            gOver = myfont.render('Game Over! (R)etry or (Q)uit' , 4, (255,255,255))
            screen.fill(black)
            screen.blit(gOver, (100, 300))
            screen.blit(score, (200, 100))
            screen.blit(lineClear, (200, 150))
            pygame.display.flip()
			
            while retry == 0:
                events = pygame.event.get()
                for event in events:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            retry = 1
                        if event.key == pygame.K_q:
                            pygame.quit()
                            sys.exit()

