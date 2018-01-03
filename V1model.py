### Import libraries
import numpy as np
import random

### Build functions 
def readSeq(filename):  #function read in a sequence (e.g. to test a fixed sequence)
    f = open(filename)
    content = f.readlines()
    num_stim = len(content)-1
    stims = np.zeros(num_stim)
    for t in range(0,num_stim):
        line = content[t+1]
        trial,stim = line.split(',')
        stims[t] = stim.strip()
    return(stims)

def degDiff(a,b): #function to calculate distance in circular space
    diff =  a - b
    diff[diff > 90.0] = diff[diff > 90.0] - 180
    diff[diff < -90.0] = 180 + diff[diff < -90.0]
    return(diff)

def memPotential(Jf,pref,stim,sigf): # formulae from Teich and Qian (2003)
    diffs = degDiff(pref,stim)
    return(Jf * np.exp( (-(diffs)**2)/(2*sigf**2)    )  )

def rand(items): # to generate a noise vector
    return( np.array([(random.random()-0.5)*2 for r in range(items)]) )

def cosd(d): # just a degree form of cosine for convenience
    return np.cos(np.radians(d))

def conn(theta,a): # connection formulae (for E and I)
    c  = (cosd(2*(theta))+1)**a
    return(c/sum(c))

def even_spread(N): # function to evenly spread stimulus/neurons across the possible orientations
    interval = 180.0/N
    return(np.linspace(interval/2.0 - 90.0,90.0 - interval/2.0,num = N))

def V_calc1(c,J,R): # calculate Ve/Vi for one neuron
    return(np.dot(c*J,R))

def V_calc2(clist,Jlist,R): # calculate Ve/Vi across the whole set of neurons
    V = np.empty(N, dtype=float)
    for n in range(N):
        V[n] = V_calc1(clist[n,:],Jlist[n],R)
    return(V)

def R_calc1(V_init,e_list,i_list,Je_list, Ji_list, R): # calculate R for one time point
        Ve = V_calc2(e_list,Je_list,R)
        Vi = V_calc2(i_list,Ji_list,R)
        V =  Ve - Vi + V_init 
        noise = rand(N) * np.mean(V) * noise_level
        R = (V+noise) * alpha
        R[R<0.0] = 0.0
        return(R)
    
def R_calc2(V_init,e_list,i_list,Je_list, Ji_list, R): # calculate R across time points
    for t in range(0,1000,tau):
        R = R_calc1(V_init,e_list,i_list,Je_list, Ji_list, R)
    return(R)

def make_stim(num_trials,prob): # make a probability sequence
    high_N = int(round(prob*num_trials))
    low_N = num_trials - high_N
    high_prob = np.round(np.random.uniform(low=-90, high=0, size=high_N))
    low_prob = np.round(np.random.uniform(low=0, high=90, size=low_N))
    stim = np.concatenate((high_prob,low_prob),axis = 0)
    return(np.random.permutation(stim))
    
def decode(fire): # for vector decoding
    fireX = np.dot(xvect,fire)/N
    fireY = np.dot(yvect,fire)/N
    return( np.degrees(np.arctan2(fireX, fireY))/2 ) # convert doubled (circular) space to axial space


def normalised_firing(R): #Normalization response of an individual neuron given summed activity 
    return(R/sum(R))

def J_update(J_orig,J,A,R,decay_rate):
    reduction = normalised_firing(R) * A # excitation reduction is based on normalised firing on trial
    J = J * (1- reduction) # excitation reduction is also scaled on what current excitation is
    decay = (J_orig-J) * decay_rate # Assuming that there is also an x% loss of reduction per trial
    J = J + decay
    J[J<0] = 0
    return(J)

# Parameters to change
num_runs  = 1000 # number of times to run the model
Ai = 0.000 # reduction of Ji
Ae = 0.010 # maximum reduction of Je
decay_rate = 0.010  # proportion decay of Je towards its original value
noise_level = 2.50 # multiplier for the noise added to the membrane potential at each time step

# Parameters that are fixed (inherited from Teich & Qian,2003)
N = 128 # number of neurons
Je_orig = 1.1 # strength of intracortical excitation 
Ji_orig = 1.1 # strength of intracortical inhibition 
Jf = 0.5 # feedforward strength 
sigf = 45.0 # feedforward tuning
ae = 2.2
ai = 1.4
tau = 15 # membrane time constant (ms)
alpha = 10.0 # spikes/s/mV

# initialize vectors
pref_list = even_spread(N) # neurons are evenly distributed
zero_index = np.argmin(abs(pref_list-(0)))
zero_pref = pref_list[zero_index]

diffs = degDiff(pref_list,zero_pref)
e  = conn(diffs,ae)
i  = conn(diffs,ai)

e_list = np.zeros(shape=(N,N))
i_list = np.zeros(shape=(N,N))
for n in range(N):
    e_list[n,:] = np.roll(e,n-zero_index) # to circle shift the numbers
    i_list[n,:] = np.roll(i,n-zero_index)
    
yvect = cosd(2*pref_list) # yaxis in double (circular) space
xvect = cosd(2*pref_list-90)  # xaxis in double (circular) space

# build a set of input stimuli with a probability distribution
for run in range(1,num_runs+1):
    side_type = random.choice([1,-1]) # decide which set of orientations is probable
    Je = [Je_orig]*N
    Ji = [Ji_orig]*N

    stims = side_type * make_stim(20,0.8) # to constrain probability in 20 trial chunks
    for i in range(20-1): # to get 400 trials in total (20 sets of 20)
        temp = side_type * make_stim(20,0.8)
        stims = np.concatenate((stims,temp),axis = 0) 

    num_trials = len(stims)  
    final_Je = np.zeros(shape=(N,len(stims)))
    final_R = np.zeros(shape=(N,len(stims)))
    decoded = np.zeros(len(stims))
    error = np.zeros(len(stims))

    ### This is the main loop where the tuning occurs
    for s in range(num_trials):
        stim = stims[s] 
        V_init = memPotential(Jf,pref_list,stim,sigf)
        noise = rand(N) * np.mean(V_init) * noise_level
        R = (V_init + noise) * alpha
        R[R<0.0] = 0.0 # floor all negative firing rates due to noise
        R = R_calc2(V_init,e_list,i_list,Je, Ji, R)
        Je = J_update(Je_orig,Je,Ae,R,decay_rate) # update Je for next trial
        Ji = J_update(Ji_orig,Ji,Ai,R,decay_rate) # no need to update Ji
        final_R[:,s] = R
        final_Je[:,s] = Je
        decoded[s] = decode(R)
        error[s] =  decoded[s] - stim

    ### Save the data of each run
    cwd = '/home/syaheed/Desktop' # change to intended path of data output
    fname = cwd + '/output/firingRate_' + str(run) + '_' + '.csv' # this is the main output
    fname2 = cwd + '/output/Je_' + str(run) + '_' + '.csv'  # Je value for every neuron at each trial

    run_c = np.ones(len(stims)) * run
    side_c = np.ones(len(stims)) * side_type
    Ae_c = np.ones(len(stims)) * Ae
    decay_c = np.ones(len(stims)) * decay_rate

    data = np.array([run_c, side_c, Ae_c, decay_c, stims, decoded, error])
    np.savetxt(fname, np.transpose(data), delimiter=',')   
    np.savetxt(fname2, np.transpose(final_Je), delimiter=',')
