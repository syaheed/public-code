import pygame, threading
from psychopy import core

pygame.init() 
pygame.joystick.init()
joy = pygame.joystick.Joystick(0)
joy.init()
joyfile = open('data.csv', 'w')

expclock = core.Clock()

class poller(threading.Thread):

    def __init__ (self):
        threading.Thread.__init__ (self)

    def run(self):
        while True:
            x = pygame.event.get()
            self.L = round(joy.get_axis(5),3) # left trigger state (from +1 to -1)
            self.R = round(joy.get_axis(4),3) # right trigger state (from +1 to -1)
            self.exClock = round(expclock.getTime(),4)
            joyfile.write(str(self.exClock) + "," + str(self.L) + "," + str(self.R) + "\n") # output the data to a csv, one row per poll
            time.sleep(0.001) # poll every 1ms

joyThread = poller()
joyThread.start()
