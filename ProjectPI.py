#!/usr/bin/env python

import pygame, random, time, math
import numpy as np
from PIL import Image

pygame.init()
pygame.mouse.set_visible(False)

pi_mode = 0
resp_timeout = 1.000

if pi_mode == 1:
 import RPi.GPIO as GPIO
 GPIO.setup(12,GPIO.OUT)
 GPIO.output(12,False)
 GPIO.output(12,True)
 path = "/home/ubuntu/Desktop/ProjectPI/"
 pygame.key.set_repeat(1,1)

else:
 pygame.key.set_repeat(1,10)
 path = "/home/s2jabar/Dropbox/Waterloo/BrittLab/ProjectPI/"

# functions

def coordfind(ori_d,xpos,ypos,csize):
    ori_r = math.radians(180-ori_d)
    xstart = xpos + (math.sin(ori_r) * csize)
    ystart = ypos + (math.cos(ori_r) * csize)
    xend = xpos - (math.sin(ori_r) * csize)
    yend = ypos - (math.cos(ori_r) * csize)
    coordlist =  [xstart,ystart,xend,yend]
    return coordlist

def rot_center(image, angle):
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image

# Definitions

infoObject = pygame.display.Info()
size= [infoObject.current_w,infoObject.current_h] # monitor resolution
centerpos = [size[0]/2,size[1]/2] # find center of screen
fixpos = [size[0]/2, size[1]/2 - 35]
default_ori = 90
stimdist = 200
gaborsize = 150
BLACK = (0,0,0)
WHITE = (255,255,255)
GRAY = (130,130,130)

error_threshold = 12
ntrial = 1000


pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=128)
sound_correct = pygame.mixer.Sound(path + "reward.wav")
sound_wrong = pygame.mixer.Sound(path + "error.wav")

screen = pygame.display.set_mode(size, pygame.FULLSCREEN|pygame.HWSURFACE|pygame.DOUBLEBUF)

done = False
screen.fill(GRAY)
pygame.display.flip()

# objects
font = pygame.font.SysFont("Monospaced",72)
fixcross = font.render("+",True, BLACK)
Gabor = pygame.image.load(path + 'gabor.bmp')
Gabor = pygame.transform.scale(Gabor,(gaborsize,gaborsize))

datafilename = path + 'timing'
datafile = open(datafilename + '.csv', 'w')
datafile.write("Trial,BlankStart,BlankElapsed,StimStart,StimElapsed,StimOri,ResOri,angDiff\n")

trial = 0
trial_start = 0

while not done:

    if pi_mode == 1:
        GPIO.output(12,False)

    csize = 50 # size of circle   
    xpos = (size[0]/2) + random.sample([-stimdist,stimdist],1)[0] 
    ypos = size[1]/2

    stimOri = random.randint(0,179)
    coord_list_actual = coordfind(stimOri,xpos,ypos,csize)

    trial = trial + 1
 
    correct = 0
    resOri = 0
    resp = 0
    resp_time = 0
    coord_list_resp = [0,0,0,0]

    #### FIX PHASE ####
    blank_time = 0
    screen.fill(GRAY)
    screen.blit(fixcross,fixpos)
    pygame.display.flip()
    blank_start = time.time()

    
    while blank_time <= 1.000 + blank_start:
        blank_time = time.time()

    #### STIMULUS PHASE ####
    stim_time = 0
    stim = rot_center(Gabor,-1*stimOri)
    screen.blit(stim,(xpos-gaborsize/2,ypos-gaborsize/2)) 
    pygame.display.update()
    stim_start = time.time()

    while stim_time <= 0.06 + stim_start:
        stim_time = time.time()

    #### DELAY PHASE ####
    blank_time2 = 0
    screen.fill(GRAY)
    screen.blit(fixcross,fixpos)
    pygame.display.flip()
    stim_time = time.time()
    blank_start2 = time.time()

    while blank_time2 <= 0.350 + blank_start2:
        blank_time2 = time.time()

    #### RESPONSE PHASE ####
    screen.fill(GRAY)
    screen.blit(fixcross,fixpos)
    pygame.display.flip()
    resp_start = time.time()
    coord_list = coordfind(default_ori,xpos,ypos,csize)
    rline = pygame.draw.line(screen,BLACK,[coord_list[0],coord_list[1]],[coord_list[2],coord_list[3]],4) # surface,color,startcoords,endcoords,width
    pygame.display.update(rline)
    e_ori = default_ori
    resOri = default_ori
    pygame.event.clear()    
    while (resp_time <= resp_timeout + resp_start) & (resp==0):
        resp_time = time.time()
        coord_list_resp = coordfind(e_ori,xpos,ypos,csize)
        screen.fill(GRAY)
        rline = pygame.draw.line(screen,BLACK,[coord_list_resp[0],coord_list_resp[1]],[coord_list_resp[2],coord_list_resp[3]],4) # surface,color,startcoords,endcoords,width
        screen.blit(fixcross,fixpos)      
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN: 
                if event.key == pygame.K_c:
                    e_ori = e_ori + 1
                elif event.key == pygame.K_z:
                    e_ori = e_ori - 1
                elif event.key == pygame.K_x:
                    resOri = e_ori
                    resp = 1
                    break
                elif event.key == pygame.K_ESCAPE:
                    done = True
                    resp = 1
                    break

    angDiff = (resOri - stimOri + 90)%180 - 90

    if abs(angDiff) <= error_threshold:
        correct = 1
        sound_correct.play(loops=0, maxtime=0,fade_ms=0)
    else:
        correct = 0
        sound_wrong.play(loops=0, maxtime=0,fade_ms=0)
        if pi_mode == 1:
            GPIO.output(12,True)

    #### FEEDBACK PHASE ####
    feed_time = 0
    coord_list_actual = coordfind(stimOri,xpos,ypos,csize)
    screen.fill(GRAY)
    aline = pygame.draw.line(screen,WHITE,[coord_list_actual[0],coord_list_actual[1]],[coord_list_actual[2],coord_list_actual[3]],4) # surface,color,startcoords,endcoords,width
    rline = pygame.draw.line(screen,BLACK,[coord_list_resp[0],coord_list_resp[1]],[coord_list_resp[2],coord_list_resp[3]],4) # surface,color,startcoords,endcoords,width    
    screen.blit(fixcross,fixpos)
    pygame.display.flip()
    feed_start = time.time()

    while feed_time <= 0.500 + feed_start:
        feed_time = time.time()

    #### DELAY PHASE ####
    blank_time3 = 0
    screen.fill(GRAY)
    screen.blit(fixcross,fixpos)
    pygame.display.flip()
    blank_start3 = time.time()

    while blank_time3 <= 0.100 + blank_start3:
        blank_time3 = time.time()

    if trial == ntrial:
            done = True
     
    dataRow = str(trial) + "," + str(blank_start) + "," + str(stim_start-blank_start) + "," + str(stim_start) + "," + str(stim_time-stim_start) + "," + str(stimOri) + "," + str(resOri) + "," + str(angDiff)
    datafile.write(dataRow + "\n")

if pi_mode == 1:
    GPIO.output(12,False)

datafile.close()
pygame.quit()



