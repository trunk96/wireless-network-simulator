import math
from scipy import constants
import util

class base_station:
    prb_bandwidth_size = 0
    total_prb = 0
    allocated_prb = 0
    ue_pb_allocation = {}
    antenna_gain = 0
    feeder_loss = 0
    antenna_power = 0
    bs_id = 0
    carrier_frequency = 0 #in MHz 
    position = None
    h_b = 40 #height of BS antenna
    number_subcarriers = 0
    env = None

    T = 10
    resource_utilization_array = [0] * T
    resource_utilization_counter = 0

    def __init__(self, bs_id, total_prb, prb_bandwidth_size, number_subcarriers, antenna_power, antenna_gain, feeder_loss, carrier_frequency, position, env):
        self.prb_bandwidth_size = prb_bandwidth_size
        self.total_prb = total_prb
        self.antenna_power = antenna_power
        self.antenna_gain = antenna_gain
        self.feeder_loss = feeder_loss
        self.bs_id = bs_id
        self.carrier_frequency = carrier_frequency
        self.position = (position[0],position[1])
        self.h_b = position[2]
        self.number_subcarriers = number_subcarriers
        self.env = env

    def compute_rbur(self):
        return sum(self.resource_utilization_array)/(self.T*self.total_prb)

    #this method will be called by an UE that tries to connect to this BS.
    #the return value will be the actual bandwidth assigned to the user
    def request_connection(self, ue_id, data_rate, rsrp):
        
        #compute SINR
        interference = 0
        for elem in rsrp:
            if elem != self.bs_id:
                interference = interference + (10 ** (rsrp[elem]/10))*util.find_bs_by_id(elem).compute_rbur()
        
        #thermal noise is computed as k_b*T*delta_f, where k_b is the Boltzmann's constant, T is the temperature in kelvin and delta_f is the bandwidth
        thermal_noise = constants.Boltzmann*293.15*list(util.bandwidth_prb_lookup.keys())[list(util.bandwidth_prb_lookup.values()).index(self.total_prb)]*1000000
        sinr = (10**(rsrp[self.bs_id]/10))/(thermal_noise + interference)
        
        r = self.prb_bandwidth_size*1000*math.log2(1+sinr) #bandwidth is in kHz
        print(r)
        N_prb = math.ceil(data_rate*1000000 / r) #data rate is in Mbps
        print(N_prb)

        if self.total_prb - self.allocated_prb <= N_prb:
            N_prb = self.total_prb - self.allocated_prb

        if ue_id not in self.ue_pb_allocation:
            self.ue_pb_allocation[ue_id] = N_prb
            self.allocated_prb += N_prb
        else:
            self.allocated_prb -= self.ue_pb_allocation[ue_id]
            self.ue_pb_allocation[ue_id] = N_prb
            self.allocated_prb += N_prb        
        return r*N_prb/1000000 #we want a data rate in Mbps, not in bps

        
    

