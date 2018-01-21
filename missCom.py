# import libraries
import pygame
import sys
import numpy as np
import random
import os 
import math

os.environ['SDL_VIDEO_CENTERED'] = '1'
clock = pygame.time.Clock()
clock.tick(60)

path = os.path.dirname(os.path.realpath(__file__))
music_names = [fn for fn in os.listdir(path)
              if any(fn.startswith (ext) for ext in ['music'])]
                          
pygame.init()
myfont = pygame.font.SysFont("monospace", 24, True)

rewardTone = pygame.mixer.Sound(path + '/' + 'reward.wav')
fireTone = pygame.mixer.Sound(path + '/' + 'fire.wav')
failTone = pygame.mixer.Sound(path + '/' + 'explode.wav')
fireTone.set_volume(0.1)
failTone.set_volume(0.3)
rewardTone.set_volume(0.9)

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
res = (900,900)
screen = pygame.display.set_mode(res)
screen.fill(black)
pygame.display.set_caption('Missle Command')
pygame.display.flip()

rad = int(res[0]*0.1)

def quitCheck():
        if event.key == pygame.K_q:          
            pygame.quit()
            sys.exit()

def drawTri(pos,col,bearing):

    cart = bear2cart(bearing)
    cart_x = cart[0] * 0.2
    cart_y = cart[1] * 0.2
    main_vert = point(cart_x+pos[0],cart_y+pos[1])

    cart = bear2cart(bearing - 90)
    cart_x = cart[0] * 0.05
    cart_y = cart[1] * 0.05
    side1_vert = point(cart_x+pos[0],cart_y+pos[1])

    cart = bear2cart(bearing + 90)
    cart_x = cart[0] * 0.05
    cart_y = cart[1] * 0.05
    side2_vert = point(cart_x+pos[0],cart_y+pos[1])
	
    pointlist = [side1_vert, main_vert, side2_vert]
    pygame.draw.polygon(screen, col, pointlist, 0)


def bear2cart(bearing):
    tang = math.tan(math.radians(bearing))
    y = 1
    x = tang/y
    dist = math.sqrt((y**2)+(x**2))
    y = y/dist
    x = x/ dist
    if bearing > 90:
        y = -y
        x = -x    
    elif bearing < -90:
        y = -y   
        x = -x
        
    if x == 0:
         x = 0.00001
    if y == 0:     
         y = 0.00001
          
    return([x,y])


def point(x,y):
    x = round((res[0]/2)*x) + res[0]/2
    y = res[1]/2 - round((res[1]/2)*y)
    return([int(x),int(y)])


def getBear(mousePos,pos):
    x = (mousePos[0] - res[0]/2.0)/(res[0]/2.0) - pos[0]
    y = -((mousePos[1] - res[1]/2.0)/(res[1]/2.0)) - pos[1]

    bearing = 90 - math.degrees(math.atan2(y,x))
    if bearing > 180:
        bearing = bearing -360
    return(bearing)


def drawAll():
    screen.fill(black)
    pygame.draw.circle(screen, gray, [int(posdeg1[0]),int(posdeg1[1])], rad, 1)
    pygame.draw.circle(screen, gray, [int(posdeg2[0]),int(posdeg2[1])], rad, 1)
    bullCount = myfont.render('Bullets: '+str(bullets), 1, (255,255,255))
    hitCount = myfont.render('Planets Saved: '+str(hit), 1, (255,255,255))
    missCount = myfont.render('Planets Destroyed: '+str(miss), 1, (255,255,255))
    screen.blit(bullCount, point(-0.9,-0.7))
    screen.blit(hitCount, point(-0.9,-0.8))
    screen.blit(missCount, point(-0.9,-0.9))
	
    mousePos = pygame.mouse.get_pos()
    draw = 0
    bearing = None
    pos = None
    col = None
    if (mousePos[0] >= posdeg1[0]-rad) & (mousePos[0] <= posdeg1[0]+rad):
        pos = pos1
        col = red
        draw = 1
    elif (mousePos[0] >= posdeg2[0]-rad) & (mousePos[0] <= posdeg2[0]+rad):
        pos = pos2
        col = blue
        draw = 1

    if draw == 1:
        if fire == 1:
            col = gray
        bearing = getBear(mousePos,pos)
        end_pt = bear2cart(bearing)
        pygame.draw.line(screen, gray, point(pos[0],pos[1]), point(end_pt[0]+pos[0],end_pt[1]+pos[1]), 1)	
        drawTri(pos,col,bearing)
	
    return(mousePos,bearing, pos, col)

col = white
pos1 = [-0.5,0]
pos2 = [0.5,0]
posdeg1 = point(pos1[0],pos1[1])
posdeg2 = point(pos2[0],pos2[1])
pos = pos1

retry = 1
hit = 0
miss = 0
bullFrames = 1000
tgtFrames = 3000
tgtScale = 1.0/tgtFrames

while retry == 1:

    n = random.choice(range(len(music_names)))
    music = music_names[n]
    pygame.mixer.music.load(path + '/' + music)
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1) 
    
    pygame.time.delay(1000)
    bullets = 20
    s = pygame.time.get_ticks()
    fire = -1
    
    hit = 0
    miss = 0
    
    while (retry == 1) & (fire == -1) & (bullets > 0):
        data = drawAll()
        pygame.display.flip()
        bearing = data[1]
        pos = data[2]
        col = data[3]
        
        tgtStart = [random.uniform(-0.5,0.5),1]
        r = random.choice([1,2])
        if r == 1:
            tgtBear = round(random.uniform(120,140))
        else:
            tgtBear = round(random.uniform(-120,-140))
        tgtVect = bear2cart(tgtBear)
        
        tgt_x = np.arange(tgtStart[0], tgtStart[0]+tgtVect[0], tgtScale*tgtVect[0])
        tgt_y = np.arange(tgtStart[1], tgtStart[1]+tgtVect[1], tgtScale*tgtVect[1])
        tframe = 0
        
        while (fire == -1):
            drawAll()
            events = pygame.event.get()
            mousePos = pygame.mouse.get_pos()
            pygame.draw.circle(screen, gray, [res[0]/2,res[1]/2], 10, 0) # target
            if (mousePos[0] < (res[0]/2) + 10) & (mousePos[0] > (res[0]/2) - 10) & (mousePos[1] > (res[1]/2) - 10) & (mousePos[1] < (res[1]/2) + 10):
                fire = 0
            pygame.display.flip()
            for event in events:
                if event.type == pygame.KEYDOWN:
                    quitCheck()
                        
        while (fire == 0):
            data = drawAll()
            bearing = data[1]
            pos = data[2]
            col = data[3]
            
            if tframe < tgtFrames:
                tgt_deg = point(tgt_x[tframe],tgt_y[tframe])
                pygame.draw.circle(screen, white, [int(tgt_deg[0]),int(tgt_deg[1])], 10, 0) # target
                tframe = tframe + 1
            else:
                bullets = bullets -1
                failTone.play()
                fire = -1
                break
                
            pygame.display.flip()       
            events = pygame.event.get()
            for event in events:

                if (event.type == pygame.MOUSEBUTTONUP) & (bearing != None) & (bullets > 0):
                    bullets = bullets -1
                    fire = 1	
                    fireTone.play()
                    fBear = bearing
                    fStart = pos
                    fCol = col              			
                    vect = bear2cart(fBear)
                
                    scale = 1.0/bullFrames
                
                    xlist = np.arange(fStart[0], fStart[0]+vect[0], scale*vect[0])
                    ylist = np.arange(fStart[1], fStart[1]+vect[1], scale*vect[1])
                    
                if event.type == pygame.KEYDOWN:
                    quitCheck()
          
        while (fire == 1):
            bframe = 0
            fire = -1
            while (bframe < bullFrames):
                events = pygame.event.get()
                pt_deg = point(xlist[bframe],ylist[bframe])
                drawAll()
                pygame.draw.circle(screen, fCol, [int(pt_deg[0]),int(pt_deg[1])], 5, 0) # bullet
                
                if tframe < tgtFrames:
                   tgt_deg = point(tgt_x[tframe],tgt_y[tframe])
                   pygame.draw.circle(screen, white, [int(tgt_deg[0]),int(tgt_deg[1])], 10, 0) # target
                   dist_x = abs(tgt_x[tframe]-xlist[bframe])
                   dist_y = abs(tgt_y[tframe]-ylist[bframe])
                   
                   if (dist_x < 0.05) & (dist_y< 0.05):
                       hit = hit + 1
                       rewardTone.play()
                       break
                   tframe = tframe + 1
                   if bframe >= bullFrames-1:
                       miss = miss + 1
                       failTone.play()
                
                pygame.display.flip()
                bframe = bframe + 1
                    
         
        if bullets <= 0:
            pygame.time.delay(1000)
            running = 0
            screen.fill(black)
            GameOver = myfont.render('Game Over! (Q)uit or (R)etry.', 4, (255,255,255))
            hitCount = myfont.render('Planets Saved: '+str(hit), 1, (255,255,255))
            screen.blit(hitCount, point(-0.3, 0.1))
            screen.blit(GameOver, point(-0.5, 0.0))
            pygame.display.flip()
            retry = 0
            
            while retry == 0:
                events = pygame.event.get()
                for event in events:
                    
                    if event.type == pygame.KEYDOWN:
                        quitCheck()
                        if event.key == pygame.K_r:          
                            retry = 1







