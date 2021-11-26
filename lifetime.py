from iqtools import *

class LifeTime():
    #going to take data from a spectogram
    #maybe averaged
    #look for the region of interest(in time) (injection)
    #look for the region of interest in frequency
    #look for small peaks and track their evol. with time (area and power)
    #area--> number of isomeric states produced
    #power-> decay, fit of the decay curve, lifetime-->Money
    def __init__(self,freq,time,power):
        self.freq=freq
        self.time=time
        self.power=power
        
    def injection(self):
        #if we observe this pattern
        #(time.min,time.max) range in time for searching decay
    def peaks(self):
        #call peakFind already done
        #get the position of the peaks etc
        #but look for the smaller ones
        #set freq range with peaks close to ground state
        #this range has to be set more with the eyes
    def tracking(self):
        #tracks evolution of peaks found in frange and trange before
        #call area_calc
        #call expo decay fitting (also to be included in pypeaks)
    def area_calc(self):
        #fit with gaussian--> get so to say (centre-3sigma,centre+3sigma)
        #calc the area under the curve between that freq range or with time???
        #implement standar integration algorithm
    def decay(self):
        #fitting of the decay of the area/power calculated
    def some_plotting(self):
        #ploting things found
        
