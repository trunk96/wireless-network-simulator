import numpy as np
from scipy import constants
import math
import util


class Satellite:
    """
    Reference: INMARSAT 4F2 ATTACHMENT 1 TECHNICAL DESCRIPTION
    Table A.12-1 - Link Budget for Signaling Forward Link from Class-1 User Terminal (200 kHz bandwidth; Spot Beam)
    """
    bs_type = "sat"
    bs_id= None
    pos = None  # tuple, (x,y) in meters
    #h = None  # height [m]
    carrier_bnd = 0.189  # carrier bandwidth [MHz]
    carrier_frequency = 1500  # frequency [MHz]
    sat_eirp = 44.5  # satellite effective isotropic radiated power [dBW]
    path_loss = 188.4  # path loss [dB]
    atm_loss = 0.1  # mean atmospheric loss [dB]
    ut_G_T = -9.7  # user terminal G/T [dB/K]
    #boltzmann_const = 10*math.log10(constants.Boltzmann)  # Boltzmann Constant [dBW/K/Hz]
    dw_path_CN0 = 74.9  # Down-path C/N_0 (carrier power to noise power spectral density) [dBHz]
    #adj_channel_int = 0.2  # adjacent channel interference [dB]
    env = None
    #rsrp = subcarrier_pow + antenna_gain - path_loss - atm_loss - adj_channel_int  # Reference Signals Received Power (for LTE)
    #rsrp = None
    #rbur = None  # resource block utilization ration


    frame_length = 120832  # [120832 symbols]
    rb_length = 288  # reference burst length, fixed [symbols]
    tb_header = 280  # traffic burst header, fixed [symbols]
    guard_space = 64  # fixed [symbols]
    total_users = 0
    frame_utilization = 0  # allocated resources
    ue_allocation = {}

    T = 10
    resource_utilization_array = [0] * T
    resource_utilization_counter = 0

    # tb_length = tb_header + n * 64 [symbols]

    def __init__(self, bs_id, position, env):
        self.bs_id = bs_id
        self.pos = (position[0], position[1])
        self.env = env
        #self.h = position[2]

    
    def compute_nsymb_SAT(self, data_rate, rsrp):
        
        #compute SINR
        interference = 0
        for elem in rsrp:
            if elem != self.bs_id and elem.bs_type == "sat":
                interference = interference + (10 ** (rsrp[elem]/10))*util.find_bs_by_id(elem).compute_rbur()
            
        thermal_noise = constants.Boltzmann*290*self.carrier_bnd*1000
        sinr = (10**(rsrp[self.bs_id]/10))/(thermal_noise + interference)

        #considering QPSK we can transmit 2 bits in one symbol
         


        return

    def request_connection(self, ue_id, data_rate, rsrp):
        # this method will be called by an UE that tries to connect to this satellite.
        # the return value will be the actual datarate assigned to the user

        # the capacity is bit/s
        r = self.carrier_bnd * 1e3 * math.log2(1 + sinr)  # bandwidth is in GHz, sinr here is not in dB

        # compute the effective resources needed
        eff_res = self.rb_length + self.guard_space + self.tb_header +1
        return

    def request_disconnection(self, ue_id):
        N_prb = self.ue_allocation[ue_id]
        self.frame_utilization -= N_prb
        del self.ue_allocation[ue_id]

    def next_timestep(self):
        return

    def compute_rbur(self):
        """
        RBUR: resource block utilization ratio.
        PRB: physical resource block
        Returns
        -------
        RBUR = #PRB allocated to che cell / #PRB belonging to the cell
        """

        return sum(self.resource_utilization_array)/(self.T*self.frame_length)