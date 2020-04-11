import numpy as np
from scipy import constants
import math
import util


class Satellite:
    """
    Reference: INMARSAT 4F2 ATTACHMENT 1 TECHNICAL DESCRIPTION, 
    Table A.12-1 - Link Budget for Signaling Forward Link from Class-1 User Terminal (200 kHz bandwidth; Spot Beam)
    TDMA is taken from the example at section 6.6.2 on "Satellite Communication Systems - Systems, Techniques and Technologies, Gérard Maral, Michel Bousquet"
    The values are adapted in order to have at least 1bit per symbol with typical SNR values (reference papers: 
    -High Throughput Satellite Systems: An Analytical Approach, H. FENECH, Fellow, IEEE, S. AMOS, A. TOMATIS, V. SOUMPHOLPHAKDY
    -High Throughput Satellites - Delivering future capacity needs, ADL)
    """
    bs_type = "sat"
    bs_id= None
    position = None  # tuple, (x,y) in meters
    #h = None  # height [m]
    carrier_bnd = 220  # carrier bandwidth [MHz]
    carrier_frequency = 28.4  # frequency [GHz]
    sat_eirp = 62 #45.1  # satellite effective isotropic radiated power [dBW]
    path_loss = 188.4  # path loss [dB]
    atm_loss = 0.1  # mean atmospheric loss [dB]
    ut_G_T = -9.7  # user terminal G/T [dB/K]
    #boltzmann_const = 10*math.log10(constants.Boltzmann)  # Boltzmann Constant [dBW/K/Hz]
    #dw_path_CN0 = 93.8  # Down-path C/N_0 (carrier power to noise power spectral density) [dBHz]
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
    frame_duration = 2 # lenght of the frame in milliseconds
    total_symbols = (frame_length - 288*2 - 64*2)/3 # in a frame there are 2 reference burst made of 288 symbols each, with a guard time of 64 symbols between them and between any other burst
    frame_utilization = 0  # allocated resources
    ue_allocation = {}

    T = 10
    resource_utilization_array = [0] * T
    resource_utilization_counter = 0

    # tb_length = tb_header + n * 64 [symbols]

    def __init__(self, bs_id, position, env):
        self.bs_id = bs_id
        self.position = (position[0], position[1])
        self.env = env
        #self.h = position[2]

    
    def compute_nsymb_SAT(self, data_rate, rsrp):
        
        #compute SINR
        interference = 0
        for elem in rsrp:
            if elem != self.bs_id and util.find_bs_by_id(elem).bs_type == "sat":
                interference = interference + (10 ** (rsrp[elem]/10))*util.find_bs_by_id(elem).compute_rbur()
            
        thermal_noise = constants.Boltzmann*290*self.carrier_bnd*1000000
        sinr = (10**(rsrp[self.bs_id]/10))/(thermal_noise + interference)
        r = self.carrier_bnd * 1000000 * math.log2(1 + sinr)

        r = r / self.frame_length # this is the data rate in [b/s] that is possible to obtains for a single symbol assigned every time frame

        r_64 = r * 64 # we can transmit in blocks of 64 symbols

        n_symb = math.ceil(data_rate*1000000 / r_64) * 64
        return n_symb, r


    def request_connection(self, ue_id, data_rate, rsrp):
        # this method will be called by an UE that tries to connect to this satellite.
        # the return value will be the actual datarate assigned to the user

        #IMPORTANT: there must always be a guard space to be added to each allocation. This guard space is included  
        # in the frame utilization but not in the ue_allocation dictionary

        N_symb, r = self.compute_nsymb_SAT(data_rate, rsrp)
        #print(N_symb)
        if self.total_symbols - self.frame_utilization <= self.tb_header + N_symb + self.guard_space:
            N_symb = self.total_symbols - self.frame_utilization - self.guard_space - self.tb_header
            if N_symb <= 0:
                N_symb = 0
                self.ue_allocation[ue_id] = 0
                return 0

        if ue_id not in self.ue_allocation:
            self.ue_allocation[ue_id] = self.tb_header + N_symb
            self.frame_utilization += self.tb_header + N_symb + self.guard_space
        else:
            self.frame_utilization -= self.ue_allocation[ue_id] + self.guard_space
            self.ue_allocation[ue_id] = self.tb_header + N_symb
            self.frame_utilization += self.tb_header + N_symb + self.guard_space   
        #print(r)
        #print(N_symb)
        return r*N_symb/1000000 #we want a data rate in Mbps, not in bps

    def request_disconnection(self, ue_id):
        N_symb_plus_header = self.ue_allocation[ue_id]
        self.frame_utilization -= N_symb_plus_header + self.guard_space
        del self.ue_allocation[ue_id]

    
    def update_connection(self, ue_id, data_rate, rsrp):
        # There are two cases: the first case is when an user has already some sybols allocated, the second case is when the user has no symbol allocated.
        # In the first case self.ue_allocation[ue_id] contains already the header and some symbols, so we have just to add the remaining symbols (if there is room)
        # In the second case self.ue_allocation[ue_id] is equal to 0, so we have to add the symbols, the header and the guard space. 
        # If there is no room for actual data symbols allocation (in the latter case), we still must have self.ue_allocation[ue_id]=0, since it is useless to allocate just the header and the guard space.

        N_symb, r = self.compute_nsymb_SAT(data_rate, rsrp)
        if self.ue_allocation[ue_id] != 0:
            diff = N_symb + self.tb_header - self.ue_allocation[ue_id] 
        else:
            diff = N_symb + self.tb_header + self.guard_space
        
        if self.total_symbols - self.frame_utilization >= diff:
            #there is the place for more symbols allocation (or less if diff is negative)
            self.frame_utilization += diff
            if self.ue_allocation[ue_id] != 0:
                self.ue_allocation[ue_id] += diff
            else:
                self.ue_allocation[ue_id] += diff - self.guard_space
        else:
            #there is no room for more symbols allocation
            diff = self.total_symbols - self.frame_utilization
            if self.ue_allocation[ue_id] == 0 and diff < self.guard_space + self.tb_header + 64:
                diff = 0
            elif self.ue_allocation[ue_id] == 0:
                self.frame_utilization += diff
                self.ue_allocation[ue_id] = diff - self.guard_space
            else:
                self.frame_utilization += diff
                self.ue_allocation[ue_id] += diff
        
        if self.ue_allocation[ue_id] == 0:
            return 0
        N_symb = self.ue_allocation[ue_id] - self.tb_header
        return N_symb*r/1000000 #remember that we want the result in Mbps 
        

    def next_timestep(self):
        print(self.frame_utilization)
        self.resource_utilization_array[self.resource_utilization_counter] = self.frame_utilization
        self.resource_utilization_counter += 1
        if self.resource_utilization_counter % self.T == 0:
            self.resource_utilization_counter = 0

    def compute_rbur(self):
        """
        RBUR: resource block utilization ratio.
        PRB: physical resource block
        Returns
        -------
        RBUR = #PRB allocated to che cell / #PRB belonging to the cell
        """

        return sum(self.resource_utilization_array)/(self.T*self.total_symbols)

    def new_state(self):
        return (sum(self.resource_utilization_array) - self.resource_utilization_array[self.resource_utilization_counter] + self.frame_utilization)/(self.total_symbols*self.T)
    

    def get_state(self):
        return self.total_symbols, self.frame_utilization
