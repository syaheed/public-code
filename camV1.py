import time
import pygame
import pygame.camera
import pygame.image
import numpy
import sys
from scipy import ndimage

pygame.init()
screen = pygame.display.set_mode((1024,768)) 
pygame.camera.init()
cam = pygame.camera.Camera(pygame.camera.list_cameras()[0])
cam.start()
cam_size = numpy.array([640,480])
centre = numpy.array([600,100])

### functions ###
font = pygame.font.Font('freesansbold.ttf',20)
def drawText(text,xpos,ypos,col):
    TextSurf = font.render(text, True, (col,col,col))
    TextRect = TextSurf.get_rect()
    TextRect.center = (xpos,ypos)
    screen.blit(TextSurf, TextRect)

surf = pygame.Surface((200, 200), flags=0, depth=16)
def drawImage(data,posx,posy):
    scaled = numpy.kron(data.astype(int), [[1,1],[1,1]])
    d3 = numpy.dstack([numpy.rot90(scaled, 1)]*3)
    d2 = pygame.surfarray.map_array(surf,d3)
    d2[d2 < 0] = 0
    pygame.surfarray.blit_array(surf, numpy.flipud(d2))
    screen.blit(surf,[posx,posy])

def drawFiring(fire,xpos,ypos):
    x = cartes_x * fire * 20
    y = cartes_y * fire * 20
    
    for ori in range(1,181):
            pygame.draw.line(screen, [255,255,255], (xpos-y[ori-1],ypos+x[ori-1]), (xpos+y[ori-1],ypos-x[ori-1]), 1)

def drawAll():
    x = numpy.sin(numpy.deg2rad(decode)) * 40
    y = numpy.cos(numpy.deg2rad(decode)) * 40
    LGN_p = (LGN + LGN.min())
    LGN_p = 255 * LGN_p / LGN_p.min()

    screen.fill((0,0,0))
    screen.blit(img,(0,0))
    pygame.draw.rect(screen, [0,255,0], (centre[0]-100,centre[1]+40,100,100), 1)
    pygame.draw.line(screen, [255,0,0], (centre[0]-50-x,centre[1]+90+y), (centre[0]-50+x,centre[1]+90-y), 2) 
    drawImage(retina,50,550)
    drawImage(LGN_p,300,550)
    drawFiring(fire,800,200)
    drawText('Retinal layer',90,520,255)
    drawText('LGN layer',350,520,255)
    drawText('V1 Firing',750,100,255)
    drawText('Tuning = ' + str(tuning_set[tune_no]) + ' deg', 800, 275, 255)
    drawText('Decode = ' + str(round(decode)) + ' deg', 800, 300, min([255,abs(conf*100)]))
    drawText('Phase = ' + str(phase_switch), 800, 325, 255)
    
imSize = 100.0
sigma = 10.0               
X = numpy.arange(1,imSize+1,1)
X0 = (X/imSize) - .5
Xm, Ym = numpy.meshgrid(X0, X0)
s = sigma / imSize 
def createGab(theta,lamda,phase):
    thetaRad = (theta / 180.0) *numpy.pi
    freq = imSize/lamda
    phaseRad = (phase * 2* numpy.pi)
    Xt = Xm * numpy.cos(thetaRad)
    Yt = Ym * numpy.sin(thetaRad)     
    XYt = Xt + Yt
    XYf = XYt * freq * 2*numpy.pi            
    grating = numpy.sin( XYf + phaseRad) 
    gauss = numpy.exp(-((Xm ** 2) + (Ym ** 2)) / (2 * (s) ** 2))
    gauss[gauss < 0.05] = 0
    return(grating * gauss)

def createGabMat(lamda,phase):   
    newlist = map(createGab, range(1,180+1),[lamda]*180, [phase]*180)
    return(numpy.dstack(newlist))

def tune(lamda,phase):
    filtGab = createGabMat(lamda,phase)
    totalWeight = sum(sum(abs(filtGab[:,:,1])));
    return filtGab/totalWeight

def fire_calc():    
    fire = numpy.empty((180))
    phase_switch = 0    
    for neuron in range(1,181):
        fire[neuron-1] = sum(sum( LGN * V1_w[:,:,neuron-1] )) /.04
    if abs(min(fire)) > abs(max(fire)):
        fire = -fire
        phase_switch = 1
    return fire,phase_switch

pref = numpy.arange(1,180+1,1)*2
cartes_x = numpy.sin(numpy.deg2rad(pref))
cartes_y = numpy.cos(numpy.deg2rad(pref))
def decoder(): 
    fire_x = sum(cartes_x * fire / 180)
    fire_y = sum(cartes_y * fire  / 180)
    decode = numpy.rad2deg( numpy.arctan2(fire_x,fire_y) ) /2
    if decode < 0:
        decode = decode + 180
    return decode

def find_LGN():
    LGN = (-retina)
    LGN = LGN - numpy.mean(LGN)
    t_s =  numpy.std(LGN)
    return (LGN *  (1/t_s))

def find_retina():
    temp = pygame.surfarray.array3d(img) 
    temp = numpy.mean(temp, axis=2)
    temp = temp.T
    return (temp[centre[1]+35:centre[1]+135, centre[0]-100:centre[0]])

def evtCheck(centre):
    events = pygame.event.get()
    for event in events:
        if (event.type == pygame.MOUSEBUTTONUP):
            mousePos = pygame.mouse.get_pos()
            if (mousePos[0] > 50) & (mousePos[0] < 580) & (mousePos[1] > 60) & (mousePos[1] < 430):
                centre[0] = int(mousePos[0]) + 60
                centre[1] = int(mousePos[1]) - 95
        elif event.type == pygame.KEYDOWN: 
            if event.key == pygame.K_q:          
                pygame.quit()
                sys.exit()
    return (centre)     

### Initialise ###
decode = 90
conf = 0
tune_no = 0
phase_no = 0

tuning_set = range(10,4,-2)
phase_set = [0.25,0.5,0.75,1.0]
max_tune_no = len(tuning_set)
max_phase_no = len(phase_set)

V1_w = tune(tuning_set[tune_no],phase_set[phase_no])

wait = 0 # camera needs time to get the 1st proper image
while wait < 10:
    img = cam.get_image()
    pygame.display.flip()
    wait = wait + 1

### Main loop ###
while True:
    centre = evtCheck(centre)     
    img = cam.get_image()
    retina = find_retina()
    LGN = find_LGN()
    ### Learning logic here ###

    
    ### Decode and draw ###
    fire,phase_switch = fire_calc()
    decode = decoder()
    conf = max(fire)
    
    drawAll()
    pygame.display.flip()











