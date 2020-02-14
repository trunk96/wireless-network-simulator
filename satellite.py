# -*- coding: utf-8 -*-
"""
Created on Thu Feb 13 17:33:10 2020

@author: Manuel Donsante
"""


import numpy as np
from scipy import constants


    
admissible_carrier ={
    # bands expressed in GHz
    "c": [4, 8],
    "ku": [12, 18],
    "k": [18, 27],
    "ka": [27, 40],
    }
    

class satellite:
    # iridium satellite
    pos = None      # position x, y
    h = 0           # height [m]
    BRmax = 0       # maximum bit rate in each datalink [kbps]
    BRocc = 0       # occupied bit rate in each datalink
    BRreq = 0       # requested bit rate
    PD = 748        # packet delay [ms]
    BER = 1e-6      # bit error rate
    f = 0           # frequency [GHz]
    antenna_gain = None         # [dBm]
    antenna_power = None        # [W]
    subcarrier_power = None
    band = None


    def __init__(self, position, BRmax, BRocc, BRreq, freq, antenna_gain, antenna_power, subcarrier_power):
        self.position = (position[0],position[1])
        self.h = position[2]
        self.BRmax = BRmax
        self.BRocc = BRocc
        self.BRreq = BRreq
        if freq <= 40 and freq >= 4:
            self.f = freq
        else:
            raise Exception("Frequency not valid. Insert value from 4 to 40 GHz")
        self.antenna_gain = antenna_gain
        self.antenna_power = antenna_power
        self.subcarrier_power = subcarrier_power
        
    
    #this method will be called by an UE that tries to connect to this BS.
    #the return value will be the actual bandwidth assigned to the user
    def request_connection(self, ue_id, data_rate, rsrp):
        return
    
    def request_disconnection(self, sat_id):
        return
        
    def next_timestep(self):
        return
    
    
    def fspl_dB(self):
        # free space path loss [dB]
        # f in [hertz]
        # h im [m]
        c = constants.speed_of_light
        lamb = c/(self.f*1e9)     # from GHz to hertz
        
        L = 4*np.pi * (self.h)/lamb
        L = 20*np.log10(L)     # Convert to dB
        return L
    
     
    def eirp(self):
        # effective isotropic radiated power [dBW]
        
        return 10 * np.log10(1000 * self.antenna_power) +  self.antenna_gain
    
    

    def received_power(self):
        # in [dB]
        
        k = constants.Boltzmann
        return self.eirp() - self.fspl_dB() + 10*np.log10(k)
    
    
    
    
    