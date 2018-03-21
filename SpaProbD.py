
'''
additional notes

This is the code used for Experiment 1 of:

Jabar, S. B., and Anderson, B. (2017) Not all probabilities are equivalent: Evidence from orientation versus spatial probability learning. Journal of Experimental Psychology: Human Perception and Performance, 42, 853-867. 

http://dx.doi.org/10.1037/xhp0000354

'''


#Setup
import random, time, numpy, types, string, math
from pyglet.window import key
from psychopy import monitors, core, visual, sound, event, gui
from scipy.stats import norm
import psychopy.info

debug = 0
lab_mode = 0

expclock = core.Clock()

if lab_mode == 0:
    #genpath = 'C:/Users/Syaheed/Dropbox/Waterloo/BrittLab/SpaProb/'
    genpath = '/home/s2jabar/Dropbox/Waterloo/BrittLab/SpaProb/'
    monitorName = 'ExpMonitor'
    font_type = 'Arial'
else:
    genpath = '/usr/local/protocol/SpaProb/'
    monitorName = 'ExpMonitor'
    font_type = 'Ubuntu'
    
protocol = 'SpaProbD'
versionid = 'B'

num_local = 20 # maintain in every set of 20
num_sets = 20 # should be 20
num_prac_sets = 2 # should be 2
num_prac_local = 20 # maintain in every set of 20
brake_point = 200 # number of trials of the main task after which to break, default = 200

if debug == 0:
    myDlg = gui.Dlg(title='User Info')
    myDlg.addField('ID:')
    myDlg.addField('Version:')
    myDlg.addField('Gender (m/f):')
    myDlg.addField('Age:')
    myDlg.addField('Hand (r/l):')
    myDlg.show()  # show dialog and wait for OK or Cancel

    userid =  myDlg.data[0]
    versionid =  myDlg.data[1]
    gender =  myDlg.data[2]
    age =  myDlg.data[3]
    hand = myDlg.data[4]
    
else:
    userid = 'Debug'
    versionid = 'A'
    gender = 'male'
    age = '99'
    hand = 'left'

if versionid == 'a':
    versionid = 'A'
elif versionid == 'a':
    versionid = 'A'
elif versionid == 'b':
    versionid = 'B'
elif versionid == 'b':
    versionid = 'B'

fullScreen = True
expMonitor = monitors.Monitor(monitorName)
expWin = visual.Window(expMonitor.getSizePix(),allowGUI=True,winType='pyglet',monitor=expMonitor,units='deg',screen=0,fullscr=fullScreen, color = [0,0,0], waitBlanking = False)
scrX = expMonitor.getSizePix()[0]
scrY = expMonitor.getSizePix()[1]
myMouse = event.Mouse(win=expWin)
expWin.setMouseVisible(True)
keyState=key.KeyStateHandler()
expWin.winHandle.push_handlers(keyState)

# angle calculator
def spacebear (x,y):
    angle = math.degrees(math.atan2(x,y)) # for spatial positions from center (bearing notation)
    return(angle)

def bearDiff (estimate, true):
    errB = estimate - true
    if errB >= 180:
        errB = -1* (360 - errB)
    elif errB <= -180:
        errB = 360 + errB

def angcalc (y,x): # for orientations
    angle = -math.degrees(math.atan2(y,x)) + 90
    if angle >= 180: 
        angle = angle - 180
    elif angle < 0: 
        angle = angle + 180
    return(angle)

def pol2cart (bear,mag):
    bear_rad = math.radians(bear)
    y = mag  * math.cos(bear_rad)
    x = mag  * math.sin(bear_rad)
    cart = [round(x,3),round(y,3)]
    return(cart)

def quadrand (quad):
    bear = ((random.random() - 0.5) * 89) + quad
    return(int(round(bear)))
    
# to find scaling factor
tg_scale = 56.128
tg_power = 0.681
def tgrate(ecc, orig):
    tg = tg_scale * (ecc**tg_power)
    return tg
    
def magf(ecc,hotspot,orig):
    mag_fact = tgrate(ecc,orig) / tgrate(hotspot,2)
    return mag_fact

def size_scale(ecc,hotspot, orig):
    size = magf(ecc,hotspot,orig) * orig
    return size

def sf_scale(ecc,hotspot, orig):
    sf = orig / magf(ecc,hotspot,orig) 
    return sf

errorTone = sound.Sound(value=genpath + "code/error.wav") #200, secs=0.3)
errorTone.setVolume(0.45)
rewardTone = sound.Sound(value=genpath + "code/reward.wav")

# Testing
curtime = time.localtime()
curInfo = psychopy.info.RunTimeInfo(win = expWin)
avgFrame = curInfo['windowRefreshTimeAvg_ms'] / 1000.0 #in terms of seconds
sdFrame = curInfo['windowRefreshTimeSD_ms'] / 1000.0 #in terms of seconds
resolution = str(scrX) + ',' + str(scrY) 

# Params
dot_size = 0.10
textSize = 0.75
ori_val = 90 # default starting orientation (doesn't matter)
size_val_orig = 2.0 # what the theoretical size is when at dim_dist
sf_val_orig = 4.0 # frequency per visual degree (when size of stim increases, more 'waves' seen)
xpos_val = 0.0 # set default position of stim along x-axis
ypos_val = 0.0 # set default position of stim along y-axis
dim_dist = 4.0 # shift from fixation in each dimension
ecc_mag = (2*(dim_dist**2))**0.5
x_dist = dim_dist
y_dist = dim_dist
distro_scale = 2.0 # to control the variance of the gaussian hotspot
size_val = size_val_orig # to set scaled sizes
sf_val = sf_val_orig # to set scaled sizes
fixspotsize = 1.2 # size of fixaion spot / click symbol
ori_errorThreshold = 12
spa_errorThreshold = 1.0
len_errorThreshold = 100
mvtThreshold = 0.05
bearThreshold = 36
click_thresh = 1.00 # ran at 0.25 tolerance for trial initiation clicks

if debug == 0:
    fITI = round(0.15/avgFrame) #inter-trial frames (blank), 0.3
    ffix = round(0.5/avgFrame) #fixation frames, 0.5
    fstim = round(0.06/avgFrame) #stim frames, 0.06
    ffeed = round(0.35/avgFrame) # feedback frames prac only), 0.35
    ftimeout = round(7.0/avgFrame) #frames response will be available to make, 7.0
    
else:
    fITI = round(0.01/avgFrame) #inter-trial frames (blank), 0.3
    ffix = round(0.01/avgFrame) #fixation frames, 0.5
    fstim = round(0.01/avgFrame) #stim frames, 0.06
    ffeed = round(0.01/avgFrame) # feedback frames prac only), 0.35
    ftimeout = round(0.01/avgFrame) #frames response will be available to make, 7.0
    
# Setup
datafilename = genpath + 'data/' + protocol + '_' + versionid + '_' + userid + '_' + time.strftime("%Y%m%d_%H%M", curtime)
datafile = open(datafilename + '.csv', 'w')
mousefile = open(datafilename + '_mouse.csv', 'w')
infofile = open(datafilename + '.info', 'w')
infofile.write(str(curInfo))
infofile.close()
    
# Stimuli
fix = visual.TextStim(expWin, units = 'deg', text = '+', ori = 0, font = font_type, height = fixspotsize, color='black', pos = [0,0.1])
click_symbol = visual.TextStim(expWin, units = 'deg', height = fixspotsize, text = '+',  ori = 45, font = font_type, color='black', pos = [0.1,0.1])
stim = visual.PatchStim(expWin, tex="sin", mask = "circle", texRes = 512, size= [size_val_orig,size_val_orig], sf = [sf_val,0], ori = ori_val, pos = [0.0,0.0],  colorSpace='rgb', color= [1, 1, 1], contrast = 0.5 )
repline = visual.ShapeStim(expWin,vertices = numpy.array([ (0,-1),(0,1)]),lineWidth = 3.0, lineColor = 'black', fillColor = (0.0,0.0,0.0),closeShape = False,ori = ori_val, units = 'deg', pos = [0.0,0.0])
feedline =  visual.ShapeStim(expWin,vertices = numpy.array([ (0,-1),(0,1)]),lineWidth = 3.0, lineColor = 'white', fillColor = (0.0,0.0,0.0),closeShape = False,ori = ori_val, units = 'deg', pos = [0.0,0.0])
small_dot = visual.Circle(expWin, radius = dot_size, pos = [0.0,0.0])
small_dot.setFillColor([-0.5,-0.5,-0.5])
small_dot.setLineColor([-0.5,-0.5,-0.5])

possible_positions = [45,135,-135,-45]
possible_positions_label = ['UR','DR','DL','UL'] # low,high, low, high

# Stimulus List Prep
if versionid == 'A':
    mu1 = 135
    mu2 = 45
else:
    mu1 = 45
    mu2 = 135

orispread = 89
num_prac = num_prac_sets * num_prac_local
num_main = num_local*num_sets

# Global initiation
stimOri_global = []
trial_global = range(1,num_prac+1) + range(1,num_main+1)
trialBlock_global = []
block_global = []
pos_label_global = []
fixcolor_global = []
xpos_global = []
ypos_global = []
dist_global = []
stimsize_global = []
stimsf_global = []
prob_global = []

for set in range(num_prac_sets):

    # Practice initiation
    stimOri_prac = []
    trial_prac = []
    trialBlock_prac = []
    block_prac = []
    pos_label_prac = []
    fixcolor_prac = []
    xpos_prac = []
    ypos_prac = []
    dist_prac = []
    stimsize_prac = []
    stimsf_prac = []
    prob_prac = []

    for local in range(num_prac_local):
        block_prac.append(0)
        fixcolor_prac.append('black')
        
        if (local >= 0) & (local < 5):
            val = possible_positions[0]
            val2 = pol2cart(val,ecc_mag)
            xpos = val2[0]
            ypos = val2[1]
            xpos_prac.append(xpos)
            ypos_prac.append(ypos)
            pos_label_prac.append(possible_positions_label[0])
            stimOri_prac.append(int(round(random.uniform(0,179))))
            prob_prac.append(0.5)
         
        elif (local >= 5) & (local < 10):
            val =  possible_positions[1]
            val2 = pol2cart(val,ecc_mag)
            xpos = val2[0]
            ypos = val2[1]
            xpos_prac.append(xpos)
            ypos_prac.append(ypos)
            pos_label_prac.append(possible_positions_label[1])
            stimOri_prac.append(int(round(random.uniform(0,179)))) 
            prob_prac.append(0.5)
            
        elif (local >= 10) & (local < 15):
            val =  possible_positions[2]
            val2 = pol2cart(val,ecc_mag)
            xpos = val2[0]
            ypos = val2[1]
            xpos_prac.append(xpos)
            ypos_prac.append(ypos)
            pos_label_prac.append(possible_positions_label[2])
            stimOri_prac.append(int(round(random.uniform(0,179)))) 
            prob_prac.append(0.5)
            
        elif (local >= 15) & (local < 19):
            val =  possible_positions[3]
            val2 = pol2cart(val,ecc_mag)
            xpos = val2[0]
            ypos = val2[1]
            xpos_prac.append(xpos)
            ypos_prac.append(ypos)
            pos_label_prac.append(possible_positions_label[3])
            stimOri_prac.append(int(round(random.uniform(0,179)))) 
            prob_prac.append(0.5)
            
        dist = math.sqrt((xpos_prac[-1]**2) + (ypos_prac[-1]**2))
        if dist < 0.01:
            dist = 0.01
        dist_prac.append(dist)
        
        size_val = size_scale(dist,dim_dist,size_val_orig)
        stimsize_prac.append(size_val)
        
        sf_val = sf_scale(dist,dim_dist, sf_val_orig)
        stimsf_prac.append(sf_val)
    
    stimOri_shuff = []
    trialBlock_shuff = range(1,num_prac_local+1)
    block_shuff = []
    pos_label_shuff = []
    fixcolor_shuff = []
    xpos_shuff = []
    ypos_shuff = []
    dist_shuff = []
    stimsize_shuff = []
    stimsf_shuff = []
    prob_shuff = []
    shuffle_list = random.sample(range(num_prac_local),num_prac_local)
    
    for i in range(num_prac_local):
        temp = shuffle_list[i]
        stimOri_shuff.append(stimOri_prac[temp-1])
        block_shuff.append(block_prac[temp-1])
        pos_label_shuff.append(pos_label_prac[temp-1])
        fixcolor_shuff.append(fixcolor_prac[temp-1])
        xpos_shuff.append(xpos_prac[temp-1])
        ypos_shuff.append(ypos_prac[temp-1])
        prob_shuff.append(prob_prac[temp-1])
        dist_shuff.append(dist_prac[temp-1])
        stimsize_shuff.append(stimsize_prac[temp-1])
        stimsf_shuff.append(stimsf_prac[temp-1])
        
    # Shuffle into Global Set
    trialBlock_global.extend(range(1,num_prac_local+1))
    stimOri_global.extend(stimOri_shuff)
    block_global.extend(block_shuff)
    pos_label_global.extend(pos_label_shuff)
    fixcolor_global.extend(fixcolor_shuff)
    xpos_global.extend(xpos_shuff)
    ypos_global.extend(ypos_shuff)
    prob_global.extend(prob_shuff)
    dist_global.extend(dist_shuff)
    stimsize_global.extend(stimsize_shuff)
    stimsf_global.extend(stimsf_shuff)
    
for sets in range(num_sets):
    
    # Local initiation
    stimOri_local = []
    block_local = []
    pos_label_local = []
    fixcolor_local = []
    xpos_local = []
    ypos_local = []
    dist_local = []
    stimsize_local = []
    stimsf_local = []
    prob_local= []

    for local in range(num_local):
        block_local.append(sets+1)
        fixcolor_local.append('black')
        
        if (local >= 0) & (local < 1):
            val = possible_positions[0]
            val2 = pol2cart(val,ecc_mag)
            xpos = val2[0]
            ypos = val2[1]
            xpos_local.append(xpos)
            ypos_local.append(ypos)
            pos_label_local.append(possible_positions_label[0])
            stimOri_local.append(round(mu1 + orispread*(random.random() - 0.5)))
            prob_local.append(0.2)
         
        elif (local >= 1) & (local < 5):
            val =  possible_positions[0]
            val2 = pol2cart(val,ecc_mag)
            xpos = val2[0]
            ypos = val2[1]
            xpos_local.append(xpos)
            ypos_local.append(ypos)
            pos_label_local.append(possible_positions_label[0])
            stimOri_local.append(round(mu2 + orispread*(random.random() - 0.5)))
            prob_local.append(0.8)
            
        elif (local >= 5) & (local < 6):
            val =  possible_positions[1]
            val2 = pol2cart(val,ecc_mag)
            xpos = val2[0]
            ypos = val2[1]
            xpos_local.append(xpos)
            ypos_local.append(ypos)
            pos_label_local.append(possible_positions_label[1])
            stimOri_local.append(round(mu1 + orispread*(random.random() - 0.5)))
            prob_local.append(0.2)
            
        elif (local >= 6) & (local < 10):
            val =  possible_positions[1]
            val2 = pol2cart(val,ecc_mag)
            xpos = val2[0]
            ypos = val2[1]
            xpos_local.append(xpos)
            ypos_local.append(ypos)
            pos_label_local.append(possible_positions_label[1])
            stimOri_local.append(round(mu2 + orispread*(random.random() - 0.5)))
            prob_local.append(0.8)
            
        elif (local >= 10) & (local < 11):
            val =  possible_positions[2]
            val2 = pol2cart(val,ecc_mag)
            xpos = val2[0]
            ypos = val2[1]
            xpos_local.append(xpos)
            ypos_local.append(ypos)
            pos_label_local.append(possible_positions_label[2])
            stimOri_local.append(round(mu2 + orispread*(random.random() - 0.5)))
            prob_local.append(0.2)
            
        elif (local >= 11) & (local < 15):
            val =  possible_positions[2]
            val2 = pol2cart(val,ecc_mag)
            xpos = val2[0]
            ypos = val2[1]
            xpos_local.append(xpos)
            ypos_local.append(ypos)
            pos_label_local.append(possible_positions_label[2])
            stimOri_local.append(round(mu1 + orispread*(random.random() - 0.5)))
            prob_local.append(0.8)
            
        elif (local >= 15) & (local < 16):
            val =  possible_positions[3]
            val2 = pol2cart(val,ecc_mag)
            xpos = val2[0]
            ypos = val2[1]
            xpos_local.append(xpos)
            ypos_local.append(ypos)
            pos_label_local.append(possible_positions_label[3])
            stimOri_local.append(round(mu2 + orispread*(random.random() - 0.5)))
            prob_local.append(0.2)
            
        elif (local >= 16) & (local < 19):
            val =  possible_positions[3]
            val2 = pol2cart(val,ecc_mag)
            xpos = val2[0]
            ypos = val2[1]
            xpos_local.append(xpos)
            ypos_local.append(ypos)
            pos_label_local.append(possible_positions_label[3])
            stimOri_local.append(round(mu1 + orispread*(random.random() - 0.5)))
            prob_local.append(0.8)
            
        dist = math.sqrt((xpos_local[-1]**2) + (ypos_local[-1]**2))
        if dist < 0.01:
            dist = 0.01
        dist_local.append(dist)
        
        size_val = size_scale(dist,dim_dist,size_val_orig)
        stimsize_local.append(size_val)
        
        sf_val = sf_scale(dist,dim_dist, sf_val_orig)
        stimsf_local.append(sf_val)

# Shuffle initiation
    stimOri_shuff = []
    trialBlock_shuff = range(1,num_local+1)
    block_shuff = []
    pos_label_shuff = []
    fixcolor_shuff = []
    xpos_shuff = []
    ypos_shuff = []
    dist_shuff = []
    stimsize_shuff = []
    stimsf_shuff = []
    prob_shuff = []
    shuffle_list = random.sample(range(num_local),num_local)
    
    for i in range(num_local):
        temp = shuffle_list[i]
        stimOri_shuff.append(stimOri_local[temp-1])
        block_shuff.append(block_local[temp-1])
        pos_label_shuff.append(pos_label_local[temp-1])
        fixcolor_shuff.append(fixcolor_local[temp-1])
        xpos_shuff.append(xpos_local[temp-1])
        ypos_shuff.append(ypos_local[temp-1])
        prob_shuff.append(prob_local[temp-1])
        dist_shuff.append(dist_local[temp-1])
        stimsize_shuff.append(stimsize_local[temp-1])
        stimsf_shuff.append(stimsf_local[temp-1])

# Shuffle into Global Set
    stimOri_global.extend(stimOri_shuff)
    block_global.extend(block_shuff)
    trialBlock_global.extend(trialBlock_shuff)
    pos_label_global.extend(pos_label_shuff)
    fixcolor_global.extend(fixcolor_shuff)
    xpos_global.extend(xpos_shuff)
    ypos_global.extend(ypos_shuff)
    prob_global.extend(prob_shuff)
    dist_global.extend(dist_shuff)
    stimsize_global.extend(stimsize_shuff)
    stimsf_global.extend(stimsf_shuff)
    
datafile.write("Subject,Gender,Age,Handedness,Experiment,Version,Debug,Lab,MvtThres,InitX,InitY,InitDist,InitBear,TrueBear,bearError,abs_bearError,bearThreshold,bear_valid,IT,Trial,Block,TrialBlock,FixColor,StimPos,StimOri,ResOri,XPos,YPos,Prob,Eccentricity,StimSize,TrialStart,LastFixX,LastFixY,LastFixTime,LastDispX,LastDispY,LastDispTime,TrialResp,SpaResp,OriResp,TrialClickX,TrialClickY,PosClickX,PosClickY,OriClickX,OriClickY,TrialRespTime,PosRespTime,OriRespTime,MT,sRT,oRT,RT,sACC,oACC,lACC,spaErrorX,spaErrorY,abs_spaError,spaError_type,spaError_signed,lenDiff,abs_lenDiff,angDiff,abs_angDiff,scrX,scrY,avgFrame,sdFrame,sf_orig,sf,fixspotsize,ori_threshold,pos_threshold,len_threshold,trial_threshold,fITI,ffix,fstim,ffeed,ftimeout,num_local,num_sets,num_prac_sets,ntrials\n")
mousefile.write("Subject,Block,Trial,Prob,Part,TrialTime,StimTime,MouseX,MouseY,StimX,StimY,Note\n")

ntrials = len(stimOri_global)

#Start instructions
text = visual.TextStim(expWin, units = 'deg', height = textSize, font = font_type, text = 'In this experiment, you will see brief spatial patterns, and are required to try to match the pattern as accurately as you can.\n\nTo begin a trial, click the "X" symbol. Please always keep your eyes on the centre of the screen (at the "+" sign).\n\nOn each trial, click on where you think the center of the pattern was. Then, use the mouse to draw a line that best matches its orientation.\n\nYou will first be given some practice.\n\n\nClick to start the practice trials.',color='black', pos = [0,0])
nframe = 0
wait_stop = 1
myMouse1 = 0
while (nframe < 10000000) & (debug == 0):
    text.draw()
    expWin.flip()
    nframe = nframe + 1
    while wait_stop == 1 : # to prevent accidental clicking
        core.wait(1)
        wait_stop = 0
    myMouse1, myMouse2, myMouse3 = myMouse.getPressed()
    if (myMouse1):
        break
    if keyState[key.ESCAPE] == True:
        core.quit()
        
while(myMouse1):
    myMouse1, myMouse2, myMouse3 = myMouse.getPressed()      
    
expWin.setMouseVisible(True)

# Expt Run
for trial in range(ntrials):
    
    # reintitialise on every trial
    oACC = 0
    sACC = 0
    lACC  = 0
    RT = 99999
    sRT = 99999
    oRT = 99999
    mouseori = 999
    oclick_pos= [99,99]
    sclick_pos = [99,99]
    tclick_pos = [99,99]
    trialclock = core.Clock()
    trialbegintime = expclock.getTime()*1000
    stimtime = 0
    frame = 0
    trial_click = 0
    pos_click = 0
    ori_click = 0
    tclick_time = 0
    sclick_time = 0
    oclick_time = 0
    init_bear = 999
    init_pos = [0,0]
    init_time = 0
    init_dist = 0
    true_bear = spacebear(xpos_global[trial],ypos_global[trial])
    bear_valid = 0
    bearError = 0
    abs_bearError = 0
    click_break = 0
    repline.setSize(0) # prevent redrawing of previous response if not response on present trial
    
    trial_click_label = 'NoFixClick'
    
    while frame < ftimeout:
        click_symbol.draw()
        mousepos=myMouse.getPos()
        mousedist = (((mousepos[0])**2) + ((mousepos[1])**2))**0.5
        myMouse1, myMouse2, myMouse3 = myMouse.getPressed()
        if (myMouse1) & (mousedist <= click_thresh):
            trial_click = 1
            tclick_pos=myMouse.getPos()
            tclick_time = trialclock.getTime()*1000
            trial_click_label = 'FixClick'
            click_break = 1
        if keyState[key.ESCAPE] == True:
            core.quit()
        expWin.flip()
        frame = frame +1
        mousepos=myMouse.getPos()
        trialtime = trialclock.getTime()*1000
        mouseRow = userid +  "," + str(block_global[trial]) +  "," + str(trial_global[trial]) +  "," + str(prob_global[trial]) +  "," + "Init" +  "," + str(trialtime)  +  "," + str(stimtime) +  "," + str(mousepos[0]) + "," + str(mousepos[1]) + "," + str(xpos_global[trial]) + "," + str(ypos_global[trial]) + "," + trial_click_label
        mousefile.write(mouseRow + "\n")
        
        if click_break == 1:
            break
    
    while(myMouse1):
        myMouse1, myMouse2, myMouse3 = myMouse.getPressed()
        
    frame = 0
    while frame < ffix:
       fix.draw()
       expWin.flip()
       frame = frame +1
       mousepos= myMouse.getPos()
       trialtime = trialclock.getTime()*1000
       mouseRow = userid +  "," + str(block_global[trial]) +  "," + str(trial_global[trial]) +  "," + str(prob_global[trial]) +  "," + "Fix" +  "," + str(trialtime)  +  "," + str(stimtime) +  "," + str(mousepos[0]) + "," + str(mousepos[1]) + "," + str(xpos_global[trial]) + "," + str(ypos_global[trial]) + "," + 'Fixing'
       mousefile.write(mouseRow + "\n")
       if keyState[key.ESCAPE] == True:
        core.quit()
    
    last_pos_in_fix = mousepos
    last_time_in_fix = trialtime

    stim.setOri(stimOri_global[trial])
    stim.setPos([ xpos_global[trial], ypos_global[trial] ])
    stim.setSize([ stimsize_global[trial], stimsize_global[trial] ])
    stim.setSF(stimsf_global[trial])
    small_dot.setPos([ xpos_global[trial], ypos_global[trial] ])
    
    frame = 0
    stimclock = core.Clock()
    while frame < fstim:
        fix.draw()
        stim.draw()
        small_dot.draw()
        expWin.flip()
        frame = frame +1
        mousepos=myMouse.getPos()
        trialtime = trialclock.getTime()*1000
        stimtime = stimclock.getTime()*1000
        mouseRow = userid +  "," + str(block_global[trial]) +  "," + str(trial_global[trial]) +  "," + str(prob_global[trial]) +  "," + "Disp" +  "," + str(trialtime)  +  "," + str(stimtime) +  "," + str(mousepos[0]) + "," + str(mousepos[1]) + "," + str(xpos_global[trial]) + "," + str(ypos_global[trial]) + "," + 'Fixing'
        mousefile.write(mouseRow + "\n")
       
    last_pos_in_disp = mousepos
    last_time_in_disp = trialtime
    
    frame = 0
    move = 0
    initiating = 0
    click_break = 0
    initiate_label = 'Fixing'
    
    while frame < ftimeout:
        fix.draw()
        mousepos=myMouse.getPos()
        trialtime = trialclock.getTime()*1000
        stimtime = stimclock.getTime()*1000
        myMouse1, myMouse2, myMouse3 = myMouse.getPressed()
        
        mvt_dist = ((mousepos[0]-last_pos_in_disp[0])**2 + (mousepos[1]-last_pos_in_disp[1])**2)
        if (mvt_dist> mvtThreshold) & (move == 0):
            move = 1
            initiating = 1
            init_dist = mvt_dist
            init_time = stimtime
            init_pos = mousepos
            init_bear = spacebear(mousepos[0]--last_pos_in_disp[0], mousepos[1]--last_pos_in_disp[1])
            bearError = init_bear-true_bear
            abs_bearError = abs(bearError)
            if (init_bear<true_bear)&(abs_bearError >= 180):
                bearError = bearError + 360
                abs_bearError = abs(bearError)
            if (init_bear>true_bear)&(abs_bearError >= 180):
                bearError = bearError - 360
                abs_bearError = abs(bearError)
            if abs_bearError <= bearThreshold:
                bear_valid = 1
            else:
                bear_valid = 0
        if initiating == 1:
            initiate_label = 'Initiating'

        if (myMouse1) :
            pos_click = 1
            sclick_pos=myMouse.getPos()
            sclick_time = trialclock.getTime()*1000
            sRT = sclick_time-stimtime
            click_break = 1
            initiate_label = 'PosClick'
       
            
        expWin.flip()
        frame = frame +1
        mouseRow = userid +  "," + str(block_global[trial]) +  "," + str(trial_global[trial]) +  "," + str(prob_global[trial]) +  "," + "Space" +  "," + str(trialtime) +  "," + str(stimtime) +  "," + str(mousepos[0]) + "," + str(mousepos[1]) + "," + str(xpos_global[trial]) + "," + str(ypos_global[trial]) + "," + initiate_label
        mousefile.write(mouseRow + "\n")
        
        if click_break == 1:
            break
        
        initiating  = 0
        if move == 1:
            initiate_label = 'Moving'
        
    while(myMouse1):
        myMouse1, myMouse2, myMouse3 = myMouse.getPressed()
        
    frame = 0
    click_break = 0
    orienting_label = 'Orienting'
    while frame < ftimeout:              
        if pos_click == 0:
           break
        else:
           mousepos=myMouse.getPos() 
           trialtime = trialclock.getTime()*1000
           stimtime = stimclock.getTime()*1000
           mousedist = (((mousepos[0]-sclick_pos[0])**2) + ((mousepos[1]-sclick_pos[1])**2))**0.5
           mouseori = angcalc (mousepos[1]-sclick_pos[1], mousepos[0]-sclick_pos[0])
           #if mousedist < 0.01: # drawing a fixed length looks very weird.
           if mousedist < stimsize_global[trial]/2:
               repline.setSize(mousedist)
           else:
               repline.setSize(stimsize_global[trial]/2)
           repline.setPos(sclick_pos)
           repline.setOri(mouseori)
           repline.draw()
           fix.draw()
           myMouse1, myMouse2, myMouse3 = myMouse.getPressed()
           if (myMouse1) :
              oclick_time = trialclock.getTime()*1000
              oRT = oclick_time- sclick_time
              oclick_pos=myMouse.getPos()
              ori_click = 1
              orienting_label = 'OriClick'
              click_break = 1
           if keyState[key.ESCAPE] == True:
              core.quit()
              
        expWin.flip()
        frame = frame +1
        mouseRow = userid +  "," + str(block_global[trial]) +  "," + str(trial_global[trial]) +  "," + str(prob_global[trial]) +  "," + "Orient" +  "," + str(trialtime)  +  "," + str(stimtime) +  "," + str(mousepos[0]) + "," + str(mousepos[1]) + "," + str(xpos_global[trial]) + "," + str(ypos_global[trial])  +  "," + orienting_label
        mousefile.write(mouseRow + "\n")
        
        if click_break == 1:
            break
    
    MT = sRT - init_time 
    RT = sRT + oRT
    angDiff = (mouseori - stimOri_global[trial] + 90)%180 - 90
    spatialError = (((sclick_pos[0]-xpos_global[trial])**2) + ((sclick_pos[1]-ypos_global[trial])**2))**0.5
    lenError = 2*(mousedist - (stimsize_global[trial]/2))
    
    mouse_ecc =  math.sqrt(sclick_pos[0]**2 + sclick_pos[1]**2)
    if mouse_ecc > dist_global[trial]:
        spatialError_type = 'Overshoot'
        spatialError_signed = spatialError
    else:
        spatialError_type = 'Undershoot'
        spatialError_signed = -1*spatialError
    
    if spatialError <= spa_errorThreshold:
        sACC = 1
    if abs(angDiff) <= ori_errorThreshold:
        oACC = 1
    if abs(lenError) <= len_errorThreshold:
        lACC = 1
    if (sACC == 1) & (oACC==1) & (lACC==1):
        rewardTone.play()
    else:
        errorTone.play()
     
    frame = 0
    while frame < ffeed:
       fix.draw()
       feedline.setOri(stimOri_global[trial] )
       feedline.setPos([ xpos_global[trial], ypos_global[trial] ])
       feedline.setSize(stimsize_global[trial]/2)
       repline.draw()
       feedline.draw()
       expWin.flip()
       frame = frame +1
       mousepos=myMouse.getPos()
       trialtime = trialclock.getTime()*1000
       stimtime = stimclock.getTime()*1000
       mouseRow = userid +  "," + str(block_global[trial]) +  "," + str(trial_global[trial]) +  "," + str(prob_global[trial])  +  "," + "Feed" +  "," + str(trialtime)  +  "," + str(stimtime) +  "," + str(mousepos[0]) + "," + str(mousepos[1]) + "," + str(xpos_global[trial]) + "," + str(ypos_global[trial])  +  "," + "Waiting"
       mousefile.write(mouseRow + "\n")
     
    frame = 0
    while frame < fITI:
       fix.draw() 
       expWin.flip()
       frame = frame +1
       mousepos=myMouse.getPos()
       trialtime = trialclock.getTime()*1000
       stimtime = stimclock.getTime()*1000
       mouseRow = userid +  "," + str(block_global[trial]) +  "," + str(trial_global[trial]) +  "," + str(prob_global[trial]) +  "," + "ITI" +  "," + str(trialtime) + "," + str(stimtime) +  "," + str(mousepos[0]) + "," + str(mousepos[1]) + "," + str(xpos_global[trial]) + "," + str(ypos_global[trial])  +  "," + "Waiting"
       mousefile.write(mouseRow + "\n")
    
    dataRow = userid +  "," + gender +  "," + age +  "," + hand + "," + protocol + "," + versionid + ","  + str(debug) +  "," + str(lab_mode)  + "," +  str(mvtThreshold) + "," + str(init_pos[0]) + "," + str(init_pos[1]) + "," + str(init_dist) + ","  + str(init_bear)  + ","  + str(true_bear) + "," + str(bearError) + "," + str(abs_bearError) + "," + str(bearThreshold) + "," +  str(bear_valid) + "," + str(init_time) + "," + str(trial_global[trial]) + "," + str(block_global[trial]) + "," + str(trialBlock_global[trial]) +"," + str(fixcolor_global[trial]) + "," + str(pos_label_global[trial]) + "," + str(stimOri_global[trial]) + "," + str(mouseori) + "," + str(xpos_global[trial]) +  "," + str(ypos_global[trial]) +  "," + str(prob_global[trial]) + "," + str(dist_global[trial]) + "," + str(stimsize_global[trial]) +  "," + str(trialbegintime) +  "," + str(last_pos_in_fix[0]) +  ","  + str(last_pos_in_fix[1]) + "," + str(last_time_in_fix) + "," + str(last_pos_in_disp[0]) +  ","  + str(last_pos_in_disp[1]) + "," + str(last_time_in_disp) + "," + str(trial_click) + "," + str(pos_click) + "," + str(ori_click) + "," + str(tclick_pos[0]) + "," + str(tclick_pos[1]) + "," + str(sclick_pos[0]) + "," + str(sclick_pos[1]) + "," + str(oclick_pos[0]) + "," + str(oclick_pos[1])  + "," + str(tclick_time) + "," + str(sclick_time) + "," + str(oclick_time)  + "," + str(MT)  + "," + str(sRT) + "," + str(oRT) + "," + str(RT) + "," + str(sACC) + "," + str(oACC) + "," + str(lACC) + "," + str(sclick_pos[0]-xpos_global[trial]) + "," + str(sclick_pos[1]-ypos_global[trial]) + "," + str(spatialError) + "," + spatialError_type + "," + str(spatialError_signed) + "," + str(lenError) + "," + str(abs(lenError)) + "," + str(angDiff) + "," + str(abs(angDiff)) + "," + resolution + "," + str(avgFrame*1000) + "," + str(sdFrame*1000)+ "," + str(sf_val_orig ) + "," + str(stimsf_global[trial]) +  "," + str(fixspotsize)+ "," + str(ori_errorThreshold)+ "," + str(spa_errorThreshold)+ "," + str(len_errorThreshold) + "," + str(click_thresh) +   ","  + str(fITI)+ "," + str(ffix) + "," + str(fstim) + "," + str(ffeed) + "," + str(ftimeout) + "," + str(num_local) + "," + str(num_sets) + "," + str(num_prac_sets) + "," + str(ntrials)
    datafile.write(dataRow + "\n")
    event.clearEvents()
    
    #End Prac instructions
    if (trial_global[trial]== num_prac) & (block_global[trial]==0) & (debug==0):
        text = visual.TextStim(expWin, units = 'deg', height = textSize,  font = font_type, text = 'You have completed the practice trials.\n\nIf you have any queries, please alert the experimenter.\n\nOtherwise, you may click to continue to the main experiment.',color='black', pos = [0,0])
        nframe = 0
        wait_stop = 1
        while nframe < 10000000:
            text.draw()
            expWin.flip()
            nframe = nframe + 1
            if wait_stop == 1 : # to prevent accidental clicking
                core.wait(3)
                wait_stop = 0
            myMouse1, myMouse2, myMouse3 = myMouse.getPressed()
            if (myMouse1):
                break
                
     # Break instructions
    if (trial_global[trial]== brake_point)&(debug==0):
        text = visual.TextStim(expWin, units = 'deg', height = textSize, font = font_type, text =  'You may take a short break.\n\nClick to continue with the experiment.', color='black', pos = [0,0])
        nframe = 0
        wait_stop = 1
        while nframe < 10000000:
            text.draw()
            expWin.flip()
            nframe = nframe + 1
            if wait_stop == 1 : # to prevent accidental clicking
                core.wait(3)
                wait_stop = 0
            myMouse1, myMouse2, myMouse3 = myMouse.getPressed()
            if (myMouse1):
                while(myMouse1):
                    myMouse1, myMouse2, myMouse3 = myMouse.getPressed()      
                break
                
#End instructions
text = visual.TextStim(expWin, units = 'deg', height = textSize, font = font_type, text = 'You have completed this portion of the experiment.\n\nPlease notify the experimenter.', color='black', pos = [0,0])
nframe = 0
wait_stop = 1
while (nframe < 10000000) & (debug == 0):
    text.draw()
    expWin.flip()
    nframe = nframe + 1
    while wait_stop == 1 : # to prevent accidental clicking
        core.wait(3)
        wait_stop = 0
    myMouse1, myMouse2, myMouse3 = myMouse.getPressed()
    if (myMouse1):
        break
core.quit() 
