import math
from scipy import constants
import util

LTEbandwidth_prb_lookup = {
    1.4: 6,
    3: 15,
    5: 25,
    10: 50,
    15: 75,
    20: 100
}

class LTEBaseStation:
    bs_type = "lte"

    def __init__(self, bs_id, total_prb, prb_bandwidth_size, number_subcarriers, antenna_power, antenna_gain, feeder_loss, carrier_frequency, position, env):
        if position[2] > 200 or position[2] < 30:
            raise Exception("COST-HATA model requires BS height in [30, 200]m")
        
        if (carrier_frequency < 150 or carrier_frequency > 2000):
            raise Exception("your results may be incorrect because your carrier frequency is outside the boundaries of COST-HATA path loss model")
        
        self.prb_bandwidth_size = prb_bandwidth_size
        self.total_prb = total_prb
        self.allocated_prb = 0
        self.antenna_power = antenna_power
        self.antenna_gain = antenna_gain
        self.feeder_loss = feeder_loss
        self.bs_id = bs_id
        self.carrier_frequency = carrier_frequency
        self.position = (position[0],position[1])
        self.h_b = position[2]
        self.number_subcarriers = number_subcarriers
        self.env = env
        self.ue_pb_allocation = {}
        self.T = 10
        self.resource_utilization_array = [0] * self.T
        self.resource_utilization_counter = 0

    def compute_rbur(self):
        return sum(self.resource_utilization_array)/(self.T*self.total_prb)

    
    def compute_nprb_LTE(self, data_rate, rsrp):
        
        #compute SINR
        interference = 0
        for elem in rsrp:
            if elem != self.bs_id and util.find_bs_by_id(elem).bs_type != "sat":
                interference = interference + (10 ** (rsrp[elem]/10))*util.find_bs_by_id(elem).compute_rbur()
        
        #thermal noise is computed as k_b*T*delta_f, where k_b is the Boltzmann's constant, T is the temperature in kelvin and delta_f is the bandwidth
        thermal_noise = constants.Boltzmann*293.15*list(LTEbandwidth_prb_lookup.keys())[list(LTEbandwidth_prb_lookup.values()).index(self.total_prb / 10)]*1000000*self.compute_rbur()
        sinr = (10**(rsrp[self.bs_id]/10))/(thermal_noise + interference)
        
        r = self.prb_bandwidth_size*1000*math.log2(1+sinr) #bandwidth is in kHz
        #with a single PRB we transmit just 1ms each 10ms (that is the frame lenght), so the actual rate is divided by 10
        r = r / 10
        N_prb = math.ceil(data_rate*1000000 / r) #data rate is in Mbps
        return N_prb, r

    #this method will be called by an UE that tries to connect to this BS.
    #the return value will be the actual bandwidth assigned to the user
    def request_connection(self, ue_id, data_rate, rsrp):
        
        N_prb, r = self.compute_nprb_LTE(data_rate, rsrp)
        if self.total_prb - self.allocated_prb <= N_prb:
            N_prb = self.total_prb - self.allocated_prb

        if ue_id not in self.ue_pb_allocation:
            self.ue_pb_allocation[ue_id] = N_prb
            self.allocated_prb += N_prb
        else:
            self.allocated_prb -= self.ue_pb_allocation[ue_id]
            self.ue_pb_allocation[ue_id] = N_prb
            self.allocated_prb += N_prb   
        print(N_prb)
        return r*N_prb/1000000 #we want a data rate in Mbps, not in bps

    def request_disconnection(self, ue_id):
        N_prb = self.ue_pb_allocation[ue_id]
        self.allocated_prb -= N_prb
        del self.ue_pb_allocation[ue_id]

    
    def update_connection(self, ue_id, data_rate, rsrp):

        N_prb, r = self.compute_nprb_LTE(data_rate, rsrp)
        diff = N_prb - self.ue_pb_allocation[ue_id]
        if self.total_prb - self.allocated_prb >= diff:
            #there is the place for more PRB allocation (or less if diff is negative)
            self.allocated_prb += diff
            self.ue_pb_allocation[ue_id] += diff
        else:
            #there is no room for more PRB allocation
            diff = self.total_prb - self.allocated_prb
            self.allocated_prb += diff
            self.ue_pb_allocation[ue_id] += diff
        N_prb = self.ue_pb_allocation[ue_id]
        return N_prb*r/1000000 #remember that we want the result in Mbps   

    #things to do before moving to the next timestep
    def next_timestep(self):
        self.resource_utilization_array[self.resource_utilization_counter] = self.allocated_prb
        self.resource_utilization_counter += 1
        if self.resource_utilization_counter % self.T == 0:
            self.resource_utilization_counter = 0

    def new_state(self):
        return (sum(self.resource_utilization_array) - self.resource_utilization_array[self.resource_utilization_counter] + self.allocated_prb)/(self.total_prb*self.T)
    
    def get_state(self):
        return self.total_prb, self.allocated_prb
    
    def get_connection_info(self, ue_id):
        return self.ue_pb_allocation[ue_id], self.total_prb
    
    def get_connected_users(self):
        return list(self.ue_pb_allocation.keys())

    def reset(self):
        self.resource_utilization_array = [0] * self.T
        self.resource_utilization_counter = 0
        
    

