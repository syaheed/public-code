'''

Code used in "Experiment 1-ori" of:

Jabar, S. B., Filipowicz, A. and Anderson, B. (2017). Knowing where is different from knowing what. Distinct response time profiles and accuracy effects for target location, orientation, and color probability. Attention, Perception, & Psychophysics. 
https://doi.org/10.3758/s13414-017-1412-8


To launch the experiment:

1) unplug and replug controller anytime before the driver is initiated 

2) open a terminal and initiate xbox driver (this is for the analog triggers)
- sudo xboxdrv -d -D --silent --dbus auto

3) open ANOTHER terminal and paste in:
- sudo ip link set eno1 up  (this is for the eyetracking)
- sudo ip addr add 100.1.1.2/24 dev eno1
- python2 /usr/local/lab/protocol/ProbIt/code/ProbItA.py 
(make sure to run a sudo command prior to running the code because the rumble feature requires root access)

'''

#Setup
import random, time, numpy, types, string, math, threading, os, signal, pygame
from psychopy import monitors, core, visual, sound, event, gui, info
from scipy.stats import norm
import psychopy.info
from psychopy.tools.monitorunittools import deg2pix
from pyglet.window import key

pid = os.getpid()
core.wait(0.5)
genpath = '/usr/local/lab/protocol/ProbIt/'

protocol = 'ProbitA'
monitorName = 'ExpMonitor'
font_type = 'Calibri'
expMonitor = monitors.Monitor(monitorName)
Resolution = expMonitor.getSizePix()
scrX = Resolution[0]
scrY = Resolution[1]
scrx = int(Resolution[0])
scry = int(Resolution[1])

pygame.init() 
pygame.display.set_mode((scrx, scry)) # initiate a blank pygame screen to activie the joystick module

from psychopy import prefs
prefs.general['audioLib'] = ['pygame']
errorTone = sound.Sound(value=genpath + "code/error.wav") #200, secs=0.3)
errorTone.setVolume(0.45)
rewardTone = sound.Sound(value=genpath + "code/reward.wav")

pygame.joystick.init()
joy = pygame.joystick.Joystick(0)
joy.init()
joy_thresh = -0.7

lab = 1
cd = 32
gazeCont = 1
fix_thresh = 50
eye_timeout = 3.0

expclock = core.Clock()
trialclock = core.Clock()
trial = 0
totalTrial = 0
phase = 'start'
type = 'prac'
pos_label = 'start'
ori = 0
prob = 0
colour = 'start'
colour1 = 'start'
colour2 = 'start'
resp = 0

if lab == 1:
    genpath = '/usr/local/lab/protocol/ProbIt/'
    import pylink as pl
    core.wait(0.5)

    def eyeTrkInit (sp):
        el = pl.EyeLink("100.1.1.1")
        el.sendCommand("screen_pixel_coords = 0 0 %d %d" %sp)
        el.sendMessage("DISPLAY_COORDS  0 0 %d %d" %sp)
        el.sendCommand("select_parser_configuration 0")
        el.sendCommand("scene_camera_gazemap = NO")
        el.sendCommand("pupil_size_diameter = %s"%("YES"))
        return(el)

#Calibrate Eyetracker - el is eytracker object, sp is screen position, cd screen luminance (?)
    def eyeTrkCalib (el,sp,cd):
        os.system('sudo xboxdrvctl -s 0 -r 0:0 &')
        pl.openGraphics(sp,cd)
        pygame.mouse.set_visible(False)
        pl.setCalibrationColors((255,255,255),(120,120,120)) # (target),(background)
        pl.setTargetSize(int(sp[0]/70), int(sp[1]/300)) # int(sp[0]/70), int(sp[1]/300)
        pl.setCalibrationSounds("","","")
        pl.setDriftCorrectSounds("","off","off")
        el.doTrackerSetup() #Launches the 'Camera Setup' in Eyelink - from there do the calibration on the eyelink computer
        pl.closeGraphics()

    # Opens edf data file - make sure a datafile name does not exceed 6 characters (or else you get bad value error)
    def eyeTrkOpenEDF (dfn,el):
        el.openDataFile(dfn + '.EDF')

    def eyeQuit(edf_fn,el):
        el.stopRecording()
        core.wait(0.5)
        el.setOfflineMode()
        core.wait(0.5)
        el.closeDataFile()
        el.close()
        pl.closeGraphics()

else:
    genpath = '/usr/local/lab/protocol/ProbIt/'

myDlg = gui.Dlg(title='User Info')
myDlg.addField('ID (number):')
myDlg.addField('Gender (m/f):')
myDlg.addField('Age:')
myDlg.addField('Hand (r/l):')
myDlg.addField('Eye Dominance (R/L):')
myDlg.show()  # show dialog and wait for OK or Cancel

userid =  myDlg.data[0]
gender =  myDlg.data[1]
age =  myDlg.data[2]
hand = myDlg.data[3]
eyeDom = myDlg.data[4]

if userid == '':
    userid = 999

expWin = visual.Window(Resolution,allowGUI=False,winType='pyglet',monitor=expMonitor,units='deg',screen=0,fullscr=False, color = [0,0,0], waitBlanking = True)
expWin.setMouseVisible(False)
keyState=key.KeyStateHandler()
expWin.winHandle.push_handlers(keyState)

#########################
# Set Probability order #
#########################

probType = int(userid)%8 #should be a value between 1-7

if (probType == 5) | (probType == 6):
    mu1 = 45
    mu2 = 135
    pos1 = [0,2]
    pos2 = [0,-2]
elif (probType == 7) | (probType == 0):
    mu1 = 45
    mu2 = 135
    pos2 = [0,2]
    pos1 = [0,-2]
elif (probType == 1) | (probType == 2):
    mu1 = 135
    mu2 = 45
    pos2 = [0,2]
    pos1 = [0,-2]
elif (probType == 3) | (probType == 4):
    mu1 = 135
    mu2 = 45
    pos1 = [0,2]
    pos2 = [0,-2]

# Randomly choose colours for the session
colours = ['green','blue']
colour1 = random.choice(colours)
colours.remove(colour1)
colour2 = colours[0]

curtime = time.localtime()
infofile = open(genpath + 'data/' + protocol + '_' +  str(probType) +'_'  + str(userid)  + '_' + time.strftime("%Y%m%d_%H%M", curtime) + '.info', 'w')
curInfo = psychopy.info.RunTimeInfo(win = expWin)
infofile.write(str(curInfo))
infofile.close()

avgFrame = curInfo['windowRefreshTimeAvg_ms'] / 1000.0 #in terms of seconds
sdFrame = curInfo['windowRefreshTimeSD_ms'] / 1000.0 #in terms of seconds
resolution = str(scrX) + ',' + str(scrY)
dp_conv = deg2pix(1.0,expMonitor)

###################
# List Prep #
###################

sets_local = 20
num_local = 20
orispread = 0

stimOri_list_final = []
stimpos_list_final = []
colour_list_final = []
prob_list_final = []
tilt_list_final = []
trial_list_final = []
block_list_final = []
trial_in_block_list_final = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20] * (sets_local*2 + 1)
task_list_final = []
ver_list_final = []
type_list_final = []

###################
# Practice Trials #
###################

for set in range(1):

    #initialise
    stimOri_list = []
    stimpos_list = []
    prob_list = []
    tilt_list = []
    colour_list = []
    type_list = []
    ver_list = []
    
    stimOri_list_shuff = []
    stimpos_list_shuff = []
    prob_list_shuff = []
    tilt_list_shuff = []
    colour_list_shuff = []
    type_list_shuff = []
    ver_list_shuff = []

    for i in range(num_local):
        type_list.append('prac')
        ver_list.append(probType)
        stimOri_list.append(round(random.choice([mu1,mu2]) + orispread*(random.random() - 0.5)))
        stimpos_list.append(random.choice([pos1,pos2]))
        colour_list.append(random.choice([colour1,colour2]))
        prob_list.append('0.5')

    shuffle_list = random.sample(range(num_local),num_local)
    block_list_final.extend([set+1]*(num_local))

    for i in range(num_local):
        temp = shuffle_list[i]
        stimOri_list_shuff.append(stimOri_list[temp-1])
        stimpos_list_shuff.append(stimpos_list[temp-1])
        prob_list_shuff.append(prob_list[temp-1])
        colour_list_shuff.append(colour_list[temp-1])
        type_list_shuff.append(type_list[temp-1])
        ver_list_shuff.append(ver_list[temp-1])
            
    stimOri_list_final.extend(stimOri_list_shuff)
    stimpos_list_final.extend(stimpos_list_shuff)
    prob_list_final.extend(prob_list_shuff)
    colour_list_final.extend(colour_list_shuff)
    type_list_final.extend(type_list_shuff)
    ver_list_final.extend(ver_list_shuff)
    trial_list_final.extend(range(1,(num_local)+1))

if int(userid)%2 == 1:

    ############# Ori List prep ######################
    
    for set in range(sets_local):
    
        #initialise
        stimOri_list = []
        stimpos_list = []
        prob_list = []
        tilt_list = []
        colour_list = []
        type_list = []
        ver_list = []
        
        stimOri_list_shuff = []
        stimpos_list_shuff = []
        prob_list_shuff = []
        tilt_list_shuff = []
        colour_list_shuff = []
        type_list_shuff = []
        ver_list_shuff = []
            
        for i in range(num_local):
            type_list.append('ori')
            ver_list.append(probType)
            if (i >= 0) & (i < 4):
                stimOri_list.append(round(mu1 + orispread*(random.random() - 0.5)))
                stimpos_list.append(pos1)
                prob_list.append('0.8')
                colour_list.append(colour1)
    
            elif (i >= 4) & (i < 8):
                stimOri_list.append(round(mu1 + orispread*(random.random() - 0.5)))
                stimpos_list.append(pos2)
                prob_list.append('0.8')
                colour_list.append(colour1)
    
            elif (i >= 8) & (i < 12):
                stimOri_list.append(round(mu1 + orispread*(random.random() - 0.5)))
                stimpos_list.append(pos1)
                prob_list.append('0.8')
                colour_list.append(colour2)
    
            elif (i >= 12) & (i < 16):
                stimOri_list.append(round(mu1 + orispread*(random.random() - 0.5)))
                stimpos_list.append(pos2)
                prob_list.append('0.8')
                colour_list.append(colour2)
            
            elif (i == 16) :
                stimOri_list.append(round(mu2 + orispread*(random.random() - 0.5)))
                stimpos_list.append(pos1)
                prob_list.append('0.2')
                colour_list.append(colour1)
    
            elif (i == 17) :
                stimOri_list.append(round(mu2 + orispread*(random.random() - 0.5)))
                stimpos_list.append(pos2)
                prob_list.append('0.2')
                colour_list.append(colour1)
    
            elif (i == 18) :
                stimOri_list.append(round(mu2 + orispread*(random.random() - 0.5)))
                stimpos_list.append(pos1)
                prob_list.append('0.2')
                colour_list.append(colour2)
    
            elif (i == 19) :
                stimOri_list.append(round(mu2 + orispread*(random.random() - 0.5)))
                stimpos_list.append(pos2)
                prob_list.append('0.2')
                colour_list.append(colour2)   
    
        shuffle_list = random.sample(range(num_local),num_local)
        block_list_final.extend([set+1]*(num_local))
    
        for i in range(num_local):
            temp = shuffle_list[i]
            stimOri_list_shuff.append(stimOri_list[temp-1])
            stimpos_list_shuff.append(stimpos_list[temp-1])
            prob_list_shuff.append(prob_list[temp-1])
            colour_list_shuff.append(colour_list[temp-1])
            type_list_shuff.append(type_list[temp-1])
            ver_list_shuff.append(ver_list[temp-1])
    
        stimOri_list_final.extend(stimOri_list_shuff)
        stimpos_list_final.extend(stimpos_list_shuff)
        prob_list_final.extend(prob_list_shuff)
        colour_list_final.extend(colour_list_shuff)
        type_list_final.extend(type_list_shuff)
        ver_list_final.extend(ver_list_shuff)
        trial_list_final.extend(range(1,(num_local*sets_local)+1))

    ############# Spa List prep ######################
    
    for set in range(sets_local):
    
        #initialise
        stimOri_list = []
        stimpos_list = []
        prob_list = []
        tilt_list = []
        colour_list = []
        type_list = []
        ver_list = []
              
        stimOri_list_shuff = []
        stimpos_list_shuff = []
        prob_list_shuff = []
        tilt_list_shuff = []
        colour_list_shuff = []
        type_list_shuff = []
        ver_list_shuff = []
    
        for i in range(num_local):
            type_list.append('spa')
            ver_list.append(probType)
            if (i >= 0) & (i < 4):
                stimOri_list.append(round(mu1 + orispread*(random.random() - 0.5)))
                stimpos_list.append(pos1)
                prob_list.append('0.8')
                colour_list.append(colour1)
    
            elif (i >= 4) & (i < 8):
                stimOri_list.append(round(mu1 + orispread*(random.random() - 0.5)))
                stimpos_list.append(pos1)
                prob_list.append('0.8')
                colour_list.append(colour2)
    
            elif (i >= 8) & (i < 12):
                stimOri_list.append(round(mu2 + orispread*(random.random() - 0.5)))
                stimpos_list.append(pos1)
                prob_list.append('0.8')
                colour_list.append(colour1)
    
            elif (i >= 12) & (i < 16):
                stimOri_list.append(round(mu2 + orispread*(random.random() - 0.5)))
                stimpos_list.append(pos1)
                prob_list.append('0.8')
                colour_list.append(colour2)
            
            elif (i == 16) :
                stimOri_list.append(round(mu1 + orispread*(random.random() - 0.5)))
                stimpos_list.append(pos2)
                prob_list.append('0.2')
                colour_list.append(colour1)
    
            elif (i == 17) :
                stimOri_list.append(round(mu1 + orispread*(random.random() - 0.5)))
                stimpos_list.append(pos2)
                prob_list.append('0.2')
                colour_list.append(colour2)
    
            elif (i == 18) :
                stimOri_list.append(round(mu2 + orispread*(random.random() - 0.5)))
                stimpos_list.append(pos2)
                prob_list.append('0.2')
                colour_list.append(colour1)
    
            elif (i == 19) :
                stimOri_list.append(round(mu2 + orispread*(random.random() - 0.5)))
                stimpos_list.append(pos2)
                prob_list.append('0.2')
                colour_list.append(colour2)   
    
        shuffle_list = random.sample(range(num_local),num_local)
        block_list_final.extend([set+1]*(num_local))
    
        for i in range(num_local):
            temp = shuffle_list[i]
            stimOri_list_shuff.append(stimOri_list[temp-1])
            stimpos_list_shuff.append(stimpos_list[temp-1])
            prob_list_shuff.append(prob_list[temp-1])
            colour_list_shuff.append(colour_list[temp-1])
            type_list_shuff.append(type_list[temp-1])
            ver_list_shuff.append(ver_list[temp-1])
            
        stimOri_list_final.extend(stimOri_list_shuff)
        stimpos_list_final.extend(stimpos_list_shuff)
        prob_list_final.extend(prob_list_shuff)
        colour_list_final.extend(colour_list_shuff)
        type_list_final.extend(type_list_shuff)
        ver_list_final.extend(ver_list_shuff)
        trial_list_final.extend(range(1,(num_local*sets_local)+1))

elif int(userid)%2 == 0:

        ############# Spa List prep ######################
    
    for set in range(sets_local):
    
        #initialise
        stimOri_list = []
        stimpos_list = []
        prob_list = []
        tilt_list = []
        colour_list = []
        type_list = []
        ver_list = []
              
        stimOri_list_shuff = []
        stimpos_list_shuff = []
        prob_list_shuff = []
        tilt_list_shuff = []
        colour_list_shuff = []
        type_list_shuff = []
        ver_list_shuff = []
    
        for i in range(num_local):
            type_list.append('spa')
            ver_list.append(probType)
            if (i >= 0) & (i < 4):
                stimOri_list.append(round(mu1 + orispread*(random.random() - 0.5)))
                stimpos_list.append(pos1)
                prob_list.append('0.8')
                colour_list.append(colour1)
    
            elif (i >= 4) & (i < 8):
                stimOri_list.append(round(mu1 + orispread*(random.random() - 0.5)))
                stimpos_list.append(pos1)
                prob_list.append('0.8')
                colour_list.append(colour2)
    
            elif (i >= 8) & (i < 12):
                stimOri_list.append(round(mu2 + orispread*(random.random() - 0.5)))
                stimpos_list.append(pos1)
                prob_list.append('0.8')
                colour_list.append(colour1)
    
            elif (i >= 12) & (i < 16):
                stimOri_list.append(round(mu2 + orispread*(random.random() - 0.5)))
                stimpos_list.append(pos1)
                prob_list.append('0.8')
                colour_list.append(colour2)
            
            elif (i == 16) :
                stimOri_list.append(round(mu1 + orispread*(random.random() - 0.5)))
                stimpos_list.append(pos2)
                prob_list.append('0.2')
                colour_list.append(colour1)
    
            elif (i == 17) :
                stimOri_list.append(round(mu1 + orispread*(random.random() - 0.5)))
                stimpos_list.append(pos2)
                prob_list.append('0.2')
                colour_list.append(colour2)
    
            elif (i == 18) :
                stimOri_list.append(round(mu2 + orispread*(random.random() - 0.5)))
                stimpos_list.append(pos2)
                prob_list.append('0.2')
                colour_list.append(colour1)
    
            elif (i == 19) :
                stimOri_list.append(round(mu2 + orispread*(random.random() - 0.5)))
                stimpos_list.append(pos2)
                prob_list.append('0.2')
                colour_list.append(colour2)   
    
        shuffle_list = random.sample(range(num_local),num_local)
        block_list_final.extend([set+1]*(num_local))
    
        for i in range(num_local):
            temp = shuffle_list[i]
            stimOri_list_shuff.append(stimOri_list[temp-1])
            stimpos_list_shuff.append(stimpos_list[temp-1])
            prob_list_shuff.append(prob_list[temp-1])
            colour_list_shuff.append(colour_list[temp-1])
            type_list_shuff.append(type_list[temp-1])
            ver_list_shuff.append(ver_list[temp-1])
            
        stimOri_list_final.extend(stimOri_list_shuff)
        stimpos_list_final.extend(stimpos_list_shuff)
        prob_list_final.extend(prob_list_shuff)
        colour_list_final.extend(colour_list_shuff)
        type_list_final.extend(type_list_shuff)
        ver_list_final.extend(ver_list_shuff)
        trial_list_final.extend(range(1,(num_local*sets_local)+1))

  ############# Ori List prep ######################
    
    for set in range(sets_local):
    
        #initialise
        stimOri_list = []
        stimpos_list = []
        prob_list = []
        tilt_list = []
        colour_list = []
        type_list = []
        ver_list = []
        
        stimOri_list_shuff = []
        stimpos_list_shuff = []
        prob_list_shuff = []
        tilt_list_shuff = []
        colour_list_shuff = []
        type_list_shuff = []
        ver_list_shuff = []
            
        for i in range(num_local):
            type_list.append('ori')
            ver_list.append(probType)
            if (i >= 0) & (i < 4):
                stimOri_list.append(round(mu1 + orispread*(random.random() - 0.5)))
                stimpos_list.append(pos1)
                prob_list.append('0.8')
                colour_list.append(colour1)
    
            elif (i >= 4) & (i < 8):
                stimOri_list.append(round(mu1 + orispread*(random.random() - 0.5)))
                stimpos_list.append(pos2)
                prob_list.append('0.8')
                colour_list.append(colour1)
    
            elif (i >= 8) & (i < 12):
                stimOri_list.append(round(mu1 + orispread*(random.random() - 0.5)))
                stimpos_list.append(pos1)
                prob_list.append('0.8')
                colour_list.append(colour2)
    
            elif (i >= 12) & (i < 16):
                stimOri_list.append(round(mu1 + orispread*(random.random() - 0.5)))
                stimpos_list.append(pos2)
                prob_list.append('0.8')
                colour_list.append(colour2)
            
            elif (i == 16) :
                stimOri_list.append(round(mu2 + orispread*(random.random() - 0.5)))
                stimpos_list.append(pos1)
                prob_list.append('0.2')
                colour_list.append(colour1)
    
            elif (i == 17) :
                stimOri_list.append(round(mu2 + orispread*(random.random() - 0.5)))
                stimpos_list.append(pos2)
                prob_list.append('0.2')
                colour_list.append(colour1)
    
            elif (i == 18) :
                stimOri_list.append(round(mu2 + orispread*(random.random() - 0.5)))
                stimpos_list.append(pos1)
                prob_list.append('0.2')
                colour_list.append(colour2)
    
            elif (i == 19) :
                stimOri_list.append(round(mu2 + orispread*(random.random() - 0.5)))
                stimpos_list.append(pos2)
                prob_list.append('0.2')
                colour_list.append(colour2)   
    
        shuffle_list = random.sample(range(num_local),num_local)
        block_list_final.extend([set+1]*(num_local))
    
        for i in range(num_local):
            temp = shuffle_list[i]
            stimOri_list_shuff.append(stimOri_list[temp-1])
            stimpos_list_shuff.append(stimpos_list[temp-1])
            prob_list_shuff.append(prob_list[temp-1])
            colour_list_shuff.append(colour_list[temp-1])
            type_list_shuff.append(type_list[temp-1])
            ver_list_shuff.append(ver_list[temp-1])
    
        stimOri_list_final.extend(stimOri_list_shuff)
        stimpos_list_final.extend(stimpos_list_shuff)
        prob_list_final.extend(prob_list_shuff)
        colour_list_final.extend(colour_list_shuff)
        type_list_final.extend(type_list_shuff)
        ver_list_final.extend(ver_list_shuff)
        trial_list_final.extend(range(1,(num_local*sets_local)+1))

ntrials = len(stimOri_list_final)

########################################

# Stimuli
stimsize = 2
textSize = 0.75
fix = visual.TextStim(expWin, units = 'deg', text = '+', ori = 0, font = font_type, height = textSize, color='black', pos = [0,0.0])
stim = visual.PatchStim(expWin, tex="sqr", mask = "circle", texRes = 256, size= [stimsize,stimsize], sf = [4,0],ori = 180, contrast = 1.0, opacity = 0.6)
circle = visual.Circle(expWin, radius=stimsize/2, edges=32, fillColor = (-1.0,-1.0,-1.0), lineColor = (-1.0,-1.0,-1.0) )

datafilename = genpath + 'data/' + protocol + '_' +  str(probType)  + '_' + str(userid) + '_' + time.strftime("%Y%m%d_%H%M", curtime) + '_bev.csv'
datafile = open(datafilename, 'w')
datafile.write("Subject,Type,Version,Trial,Pos,Ori,Colour,Prob,ACC,Resp,ColourLeft,ColourRight,LeftTrig,RightTrig,baseLeftTrig,baseRightTrig,IT_left,IT_Right,RT,initRight,initLeft,Recal,stimTime,respTime,eyeDom,totalTrial,Resp,avgFrame,probType,protocol,joyThresh,fixThresh,Hand,Age,Gender,ResX,ResY,dpConv\n")
datafile.flush()

joyfilename = genpath + 'data/' + protocol  + '_' +  str(probType)  + '_' + str(userid)  + '_' + time.strftime("%Y%m%d_%H%M", curtime) + '_joy.csv'
joyfile = open(joyfilename, 'w')
joyfile.write("Subject,ExptClock,TrialClock,TotalTrial,Phase,LTrig,RTrig\n")

class poller(threading.Thread):

    def __init__ (self):
        threading.Thread.__init__ (self)

    def run(self):
        while True:
            x = pygame.event.get()
            self.L = round(joy.get_axis(5),3)
            self.R = round(joy.get_axis(4),3)
            self.S = joy.get_button(7)
            self.Phase = phase
            self.totalTrial = totalTrial
            self.exClock = round(expclock.getTime(),4)
            self.trClock = round(trialclock.getTime() * 1000,1)
            joyRow = str(userid) + "," + str(self.exClock) + "," + str(self.trClock) + "," + str(self.totalTrial) + "," + str(self.Phase) + "," + str(self.L) + "," + str(self.R)
            joyfile.write(str(joyRow) + "\n")
            time.sleep(0.001)

joyThread = poller()
joyThread.start()

expWin.flip()  

if lab == 1 :
    pygame.display.toggle_fullscreen()    
    eyelink = eyeTrkInit((scrx,scry))
    edf_fn = "P" + str(userid)
    core.wait(0.5)
    eyeTrkOpenEDF(edf_fn,eyelink)
    eyeTrkCalib(eyelink,(scrx,scry),cd)
    pygame.display.toggle_fullscreen()    

    # To sync Eyetracker, Psychopy times:
    expt_start_time = expclock.getTime() # overwrite to sync with EEGtime
    message = "User " + str(userid) + " " + "Version " + str(probType) + "" + "Sync Psychopy Time " + str(expt_start_time) + " Deg2Pix " + str(dp_conv) + " Resolution " + str(scrx) + " "  + str(scry)

    eyelink.sendMessage(message)
    eyelink.startRecording(1,1,1,1)
    eyelink_starttime = pl.currentTime()


alert = visual.TextStim(expWin, units = 'deg', height = textSize, text = 'Please alert the experimenter to recalibrate the eyetracker',color='black', pos = [0,0])			    
if colour1 == 'blue':
    instr = visual.TextStim(expWin, units = 'deg', text = 'Blue = LT, Green = RT.\nSlightly hold the triggers, and press start to begin.', ori = 0, font = font_type, height = textSize, color='black', pos = [0,-4])
elif colour1 == 'green':
    instr = visual.TextStim(expWin, units = 'deg', text = 'Green = LT, Blue = RT.\nSlightly hold the triggers, and press start to begin.', ori = 0, font = font_type, height = textSize, color='black', pos = [0,-4])

core.wait(0.5)
done = 0
phase = 'inst'
while done == 0:
    instr.draw() 
    extime = joyThread.exClock

    if (joyThread.R != 0) & (joyThread.L != 0):
        if joyThread.S == 1:
            break   
 
    if keyState[key.ESCAPE] == True:
        os.system('sudo xboxdrvctl -s 0 -r 0:0')
        os.kill(pid,signal.SIGKILL)
        core.quit()
 
    expWin.flip()   

totalTrial = 0
for i in range(ntrials):
    phase = 'pfix'
    resp = 0
    trialclock = core.Clock()
    ACC = 0
    RT = -999
    totalTrial = totalTrial + 1
	
    type = type_list_final[i]
    ori = stimOri_list_final[i] 
    prob = prob_list_final[i]
    pos = stimpos_list_final[i] 
    if pos[1] > 0:
        pos_label = 'top'
    elif pos [1] < 0:
        pos_label = 'bottom'
        
    colour = colour_list_final[i] 
    if colour == 'green':
        col = [-1.0,1.0,-1.0]
    elif colour == 'blue':
        col = [-1.0,0.75,0.5]
    
	fix.setColor('black')
    stim.setPos(pos)
    stim.setOri(ori)    
    circle.setPos(pos) 
    circle.fillColor = col 

    #Drift correct midway through block
    if gazeCont == 1:
        if (i==20)|(i == 120)|(i == 220)|(i == 320)|(i == 420)|(i == 520)|(i == 620)|(i == 720):
            os.system('sudo xboxdrvctl -s 0 -r 0:0 &')
            pygame.display.toggle_fullscreen() 
            pygame.mouse.set_visible(False)
            pl.openGraphics((scrx,scry),cd)
            eyelink.doDriftCorrect(scrx/2,scry/2,1,1)
            eyelink.applyDriftCorrect()
            expWin.flip() 
            pl.closeGraphics()
            pygame.display.toggle_fullscreen() 
            eyelink.startRecording(1,1,1,1) 
        
    done = 0
    while done ==0:
        fix.draw()
        extime = joyThread.exClock
        trtime = joyThread.trClock
        rtrig = joyThread.R
        ltrig = joyThread.L

        if (rtrig<-joy_thresh) &  (ltrig<-joy_thresh) & (rtrig> joy_thresh) &  (ltrig>joy_thresh):
            break
        expWin.flip()

    frame = 0
    phase = 'fix'
    isi = random.choice(range(19,32))
    while (frame < isi) :
        fix.draw()
        extime = joyThread.exClock
        trtime = joyThread.trClock
        rtrig = joyThread.R
        ltrig = joyThread.L

        if (ltrig <joy_thresh) & (rtrig <joy_thresh):
            fix.setColor('red')
            os.system('sudo xboxdrvctl -s 0 -r 200:200 &')
        elif (rtrig <joy_thresh) & (ltrig >=joy_thresh):
            fix.setColor('red')
            os.system('sudo xboxdrvctl -s 0 -r 0:200 &')
        elif (ltrig <joy_thresh) & (rtrig >=joy_thresh):
            fix.setColor('red')
            os.system('sudo xboxdrvctl -s 0 -r 200:0 &')
        else:
            fix.setColor('black')
            os.system('sudo xboxdrvctl -s 0 -r 0:0 &')
        
        expWin.flip()
        frame = frame + 1       
        
        if keyState[key.ESCAPE] == True:
            os.system('sudo xboxdrvctl -s 0 -r 0:0')
            os.kill(pid,signal.SIGKILL)
            core.quit()

    frame = 0
    recal = 0
    eye_avail = 0
    eye_start_time = -999
    initiate_left = 0
    initiate_right = 0
    IT_left = -999
    IT_right = -999
    IT_right_time = -999
    IT_left_time = -999  
    search_time = joyThread.exClock
    
    while (gazeCont==1) & (eye_avail == 0) & (lab==1):
        sample = eyelink.getNewestSample()
        if sample != None:
            sample_time = joyThread.exClock
            eye = None
            if eyeDom == 'R':
                eye = sample.getRightEye().getGaze()
            elif eyeDom == 'L':
                eye = sample.getLeftEye().getGaze()
            eyeT = [(eye[0]-(scrx/2)),-(eye[1]-(scry/2))]	
            if (abs(eyeT[0])< fix_thresh) & (abs(eyeT[1])< fix_thresh):
                eye_avail = 1
            elif (sample_time - search_time) > eye_timeout:
                expWin.flip()
                eye_avail = 1
                recal = 1
                os.system('sudo xboxdrvctl -s 0 -r 0:0 &')	
                alert.draw()
                expWin.flip()
                core.wait(2.0)
                pygame.display.toggle_fullscreen()
                pygame.mouse.set_visible(False)
                pl.openGraphics((scrx,scry),cd)
                eyelink.doTrackerSetup()
                expWin.flip() # fix only
                pl.closeGraphics()
                pygame.display.toggle_fullscreen() 
                eyelink.startRecording(1,1,1,1)
                errorTone = sound.Sound(value=genpath + "code/error.wav") #200, secs=0.3)
                errorTone.setVolume(0.45)
                rewardTone = sound.Sound(value=genpath + "code/reward.wav")
                event.clearEvents()
                fix.draw() # repeat same fixation on next flip	
                expWin.flip() # fix only
                fix.draw() # repeat same fixation on next flip	
                expWin.flip() # fix only

    stim_time = joyThread.exClock
    
    if lab == 1:
       eyelink.sendCommand("record_status_message 'Trial %d'"%(i+1))
       message_text1 = "StimOnset " + str(stim_time) + " Trial " + str(i+1) + " PosX(deg) " + str(round(pos[0],1)) + " PosY(deg) " + str(round(pos[1],1)) + " PosX(pix) " + str(round(deg2pix(pos[0],expMonitor),1)) + " PosY(pix) " + str(round(deg2pix(pos[1],expMonitor),1)) + " Ori " + str(ori)  + " Prob " + str(prob_list_final[i]) 
       message_text2 = "Type" + str(type) + "Recalib " + str(recal)
       eyelink.sendMessage(message_text1)
       eyelink.sendMessage(message_text2)
       
    phase = 'stim'
    base_rtrig = joyThread.R
    base_ltrig = joyThread.L
     
    while (frame < 500) :
        fix.draw()
        circle.draw()
        stim.draw()
        extime = joyThread.exClock
        trtime = joyThread.trClock
        rtrig = joyThread.R
        ltrig = joyThread.L

        if initiate_right == 0:
            if (rtrig-base_rtrig) > 0.001:
                IT_right_time = joyThread.exClock
                IT_right = round((IT_right_time - stim_time)*1000,3)
                initiate_right = 1
                phase = 'init'

        if initiate_left == 0:
            if (ltrig-base_ltrig) > 0.001:
                IT_left_time = joyThread.exClock
                IT_left = round((IT_left_time - stim_time)*1000,3)
                initiate_left = 1        
                phase = 'init'
                
        if (ltrig <joy_thresh) & (rtrig <joy_thresh):
            fix.setColor('red')
            os.system('sudo xboxdrvctl -s 0 -r 200:200 &')
        elif (rtrig <joy_thresh) & (ltrig >=joy_thresh):
            fix.setColor('red')
            os.system('sudo xboxdrvctl -s 0 -r 0:200 &')
        elif (ltrig <joy_thresh) & (rtrig >=joy_thresh):
            fix.setColor('red')
            os.system('sudo xboxdrvctl -s 0 -r 200:0 &')
        elif ltrig >= -joy_thresh:
            resp = 1
            phase = 'resp'
            resp_time = joyThread.exClock
            RT = round((resp_time - stim_time)*1000,3)

            if colour2 == colour:
                ACC = 0    
                break
            elif colour1 == colour:
                ACC = 1
                break
        elif rtrig >= -joy_thresh:
            resp = 1
            phase = 'resp'
            resp_time = joyThread.exClock
            RT = round((resp_time - stim_time)*1000,3)

            if colour1 == colour:
                ACC = 0
                break               
            elif colour2 == colour:
                ACC = 1
                break           
        else:
            fix.setColor('black')
            os.system('sudo xboxdrvctl -s 0 -r 0:0 &')    
                         
        if keyState[key.ESCAPE] == True:
            os.system('sudo xboxdrvctl -s 0 -r 0:0')
            os.kill(pid,signal.SIGKILL)
            core.quit()
        
        expWin.flip()
        frame = frame +1 
        
    if resp == 1:
        if ACC == 1:
            rewardTone.play()
        elif ACC == 0:
            errorTone.play()
    else:
        errorTone.play()    
    
    trial = trial_list_final[i]
    dataRow = (str(userid) + ',' + str(type) + ',' + str(probType) + ',' + str(trial) + ',' + str(pos_label) + ',' + str(ori) + ',' + str(colour)  + ',' + str(prob)  + ',' + str(ACC) + ',' + str(resp) + ',' + str(colour1) + ',' + str(colour2) + ',' + str(ltrig) + ',' + str(rtrig) + ',' + str(base_ltrig) + ',' + str(base_rtrig) + ',' + str(IT_left) + ',' + str(IT_right) + ',' + str(RT) + ',' + str(initiate_right) + ',' + str(initiate_left) + ',' + str(recal) + ',' + str(stim_time) + ',' + str(resp_time) + ',' + str(eyeDom) + ',' + str(totalTrial) + ',' + str(resp) + ',' + str(avgFrame) + ',' + str(probType) + ',' + str(protocol) + ',' + str(joy_thresh) + ',' + str(fix_thresh) + ',' + str(hand) + ',' + str(age) + ',' + str(gender) + ',' + str(resolution) + ',' + str(dp_conv) )                
    datafile.write(dataRow + "\n")
    datafile.flush()
    joyfile.flush()

    #End Prac instructions
    if (i == 20-1) :
        phase = 'endp'
        os.system('sudo xboxdrvctl -s 0 -r 0:0 &')
        text = visual.TextStim(expWin, units = 'deg', height = textSize, text = 'You have completed the practice trials.\n\nIf you have any queries, please alert the experimenter.',color='black', pos = [0,2])
        expWin.flip()
        nframe = 0
        wait_stop = 1
        while nframe < 10000000:
            text.draw()
            instr.draw()
            expWin.flip()
            nframe = nframe + 1
            if joyThread.S == 1:
                break
                
    #Break instructions
    if (i == 400+20-1):
        phase = 'brk'
        os.system('sudo xboxdrvctl -s 0 -r 0:0 &')
        text = visual.TextStim(expWin, units = 'deg', height = textSize, text = 'You may take a short break.\n\nPress "Start" to continue with the experiment.',color='black', pos = [0,0])
        nframe = 0
        while nframe < 10000000:
            text.draw()
            expWin.flip()
            nframe = nframe + 1
            if joyThread.S == 1:
                break
        if lab == 1:
            expWin.flip()
            alert.draw()
            expWin.flip()
            core.wait(2.0)
            pygame.display.toggle_fullscreen()  	
            pl.openGraphics((scrx,scry),cd)
            eyelink.doTrackerSetup()
            expWin.flip() # fix only
            pl.closeGraphics()
            pygame.display.toggle_fullscreen()  
            eyelink.startRecording(1,1,1,1)
            errorTone = sound.Sound(value=genpath + "code/error.wav") #200, secs=0.3)
            errorTone.setVolume(0.45)
            rewardTone = sound.Sound(value=genpath + "code/reward.wav")
            event.clearEvents()
            fix.draw() # repeat same fixation on next flip	
            expWin.flip() # fix only
            fix.draw() # repeat same fixation on next flip	
            expWin.flip() # fix only
        
ending = visual.TextStim(expWin, units = 'deg', text = 'End of Experiment', ori = 0, font = font_type, height = 1.5, color='black', pos = [0,0.1])
done = 0
phase = 'end'
frame = 0
core.wait(0.5)
while frame < 50:
    ending.draw() 
    extime = joyThread.exClock  

    if (rtrig > joyThread.R) & (ltrig > joyThread.L):
        done = 1   
 
    expWin.flip()
    frame = frame + 1 

os.system('sudo xboxdrvctl -s 0 -r 0:0 &')
eyelink.sendMessage("DONE")
eyeQuit(edf_fn,eyelink)
core.wait(5.0)
os.kill(pid,signal.SIGKILL)
core.quit()
