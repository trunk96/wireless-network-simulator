import environment
import math
from scipy import constants
import util

class DroneRelay:
    bs_type = "drone_relay"

    def __init__(self, bs_id, linked_bs_id, amplification, antenna_gain, feeder_loss, carrier_frequency, position, env):
        if position[2] > 200 or position[2] < 30:
            raise Exception("COST-HATA model requires BS height in [30, 200]m")
        
        if (carrier_frequency < 150 or carrier_frequency > 2000):
            raise Exception("your results may be incorrect because your carrier frequency is outside the boundaries of COST-HATA path loss model")
        
        
        self.amplification = amplification
        self.antenna_gain = antenna_gain
        self.feeder_loss = feeder_loss
        self.bs_id = bs_id
        self.carrier_frequency = carrier_frequency
        self.fr = -1
        if (carrier_frequency <= 6000):  #below 6GHz
            self.fr = 0
        elif (carrier_frequency >= 24250 and carrier_frequency <= 52600): #between 24.25GHz and 52.6GHz
            self.fr = 1
        self.position = (position[0],position[1])
        self.current_position = self.position
        self.starting_position = position
        self.h_b = position[2]
        self.h_m = position[2]
        self.env = env

        self.linked_bs = linked_bs_id

        self.theta_k = 0

    def compute_rbur(self):
        return util.find_bs_by_id(self.linked_bs).compute_rbur()

    def compute_rsrp_drone(self, ue):
        #relay rsrp depends from the signal received by the BS and by the re-amp made by the drone
        print(util.compute_rsrp(self, util.find_bs_by_id(self.linked_bs), self.env))
        return self.amplification + util.compute_rsrp(self, util.find_bs_by_id(self.linked_bs), self.env) + self.antenna_gain - self.feeder_loss - util.compute_path_loss_cost_hata(ue, self, self.env)

    def request_connection(self, ue_id, data_rate, available_bs):
        rsrp = available_bs.copy()
        if self.bs_id in rsrp:
            value = rsrp[self.bs_id]
            del rsrp[self.bs_id]
            if self.linked_bs in rsrp:
                del rsrp[self.linked_bs]
            rsrp[self.linked_bs] = value
        return util.find_bs_by_id(self.linked_bs).request_connection(ue_id, data_rate, rsrp)

    def request_disconnection(self, ue_id):
        util.find_bs_by_id(self.linked_bs).request_disconnection(ue_id)

    def update_connection(self, ue_id, data_rate, available_bs):
        rsrp = available_bs.copy()
        if self.bs_id in rsrp:
            value = rsrp[self.bs_id]
            del rsrp[self.bs_id]
            if self.linked_bs in rsrp:
                del rsrp[self.linked_bs]
            rsrp[self.linked_bs] = value
        return util.find_bs_by_id(self.linked_bs).update_connection(ue_id, data_rate, rsrp)
    
    def next_timestep(self):
        return
    
    def new_state(self):
        return util.find_bs_by_id(self.linked_bs).new_state()
    
    def get_state(self):
        return util.find_bs_by_id(self.linked_bs).get_state()
    
    def get_connection_info(self, ue_id):
        return util.find_bs_by_id(self.linked_bs).get_connection_info(ue_id)
    
    def get_connected_users(self):
        return util.find_bs_by_id(self.linked_bs).get_connected_users()

    def reset(self):
        self.position = (self.starting_position[0], self.starting_position[1])
        self.current_position = self.position
        self.h_b = self.starting_position[2]
        self.h_m = self.starting_position[2]
        return util.find_bs_by_id(self.linked_bs).reset()

    def move(self, destination, speed):
        x_k = destination[0] - self.position[0]
        y_k = destination[1] - self.position[1]
        z_k = destination[2] - self.h_b
        theta_k = self.theta_k
        v_k = 1*(x_k*math.cos(theta_k) + y_k*math.sin(theta_k))
        v_z_k = 1*z_k
        if v_k > speed and v_k > 0:
            v_k = speed
        elif v_k < -speed and v_k < 0:
            v_k = -speed
        if v_z_k > speed and v_z_k > 0:
            v_z_k = speed
        elif v_z_k < -speed and v_z_k < 0:
            v_z_k = -speed
        w_k = 1*(math.atan2(-y_k,-x_k) - theta_k + math.pi)


        new_x = self.position[0]+v_k*math.cos(theta_k + (w_k / 2))
        new_y = self.position[1]+v_k*math.sin(theta_k + (w_k / 2))
        new_z = self.h_b + v_z_k
        new_theta = self.theta_k + w_k
        self.position = (new_x, new_y)
        self.h_b = new_z
        self.h_m = new_z
        self.current_position = self.position
        self.theta_k = new_theta

    def compute_latency(self):
        return util.find_bs_by_id(self.linked_bs).compute_latency() #TODO



#Table 5.3.3-1: Minimum guardband [kHz] (FR1) and Table: 5.3.3-2: Minimum guardband [kHz] (FR2), 3GPPP 38.104
#number of prb depending on the numerology (0,1,2,3), on the frequency range (FR1, FR2) and on the base station bandwidth
NRbandwidth_prb_lookup = {
    0:[{
        5:25,
        10:52,
        15:79,
        20:106,
        25:133,
        30:160,
        40:216,
        50:270
    }, None],
    1:[{
        5:11,
        10:24,
        15:38,
        20:51,
        25:65,
        30:78,
        40:106,
        50:133,
        60:162,
        70:189,
        80:217,
        90:245,
        100:273
    }, None],
    2:[{
        10:11,
        15:18,
        20:24,
        25:31,
        30:38,
        40:51,
        50:65,
        60:79,
        70:93,
        80:107,
        90:121,
        100:135
    },
    {
        50:66,
        100:132,
        200:264
    }],
    3:[None, 
    {
        50:32,
        100:66,
        200:132,
        400:264
    }]
}



class DroneBaseStation:
    bs_type = "drone_bs"

    def __init__(self, bs_id, total_prb, prb_bandwidth_size, number_subcarriers, numerology, antenna_power, antenna_gain, feeder_loss, carrier_frequency, total_bitrate, position, env):
        if position[2] > 200 or position[2] < 30:
            raise Exception("COST-HATA model requires BS height in [30, 200]m")
        
        if (carrier_frequency < 150 or carrier_frequency > 2000):
            raise Exception("your results may be incorrect because your carrier frequency is outside the boundaries of COST-HATA path loss model")
        
        self.prb_bandwidth_size = prb_bandwidth_size
        self.total_prb = total_prb
        self.total_bitrate = total_bitrate
        self.allocated_prb = 0
        self.allocated_bitrate = 0
        self.antenna_power = antenna_power
        self.antenna_gain = antenna_gain
        self.feeder_loss = feeder_loss
        self.bs_id = bs_id
        self.carrier_frequency = carrier_frequency
        self.fr = -1
        if (carrier_frequency <= 6000):  #below 6GHz
            self.fr = 0
        elif (carrier_frequency >= 24250 and carrier_frequency <= 52600): #between 24.25GHz and 52.6GHz
            self.fr = 1
        self.position = (position[0],position[1])
        self.starting_position = position
        self.h_b = position[2]
        self.number_subcarriers = number_subcarriers
        self.env = env
        self.numerology = numerology
        self.ue_pb_allocation = {}
        self.ue_bitrate_allocation = {}
        self.T = 10
        self.resource_utilization_array = [0] * self.T
        self.resource_utilization_counter = 0

        self.theta_k = 0



    def compute_rbur(self):
        return sum(self.resource_utilization_array)/(self.T*self.total_prb)

    
    def compute_nprb_NR(self, data_rate, rsrp):
        #compute SINR
        interference = 0
        for elem in rsrp:
            if elem != self.bs_id and util.find_bs_by_id(elem).bs_type != "sat":
                interference = interference + (10 ** (rsrp[elem]/10))*util.find_bs_by_id(elem).compute_rbur()
        
        #thermal noise is computed as k_b*T*delta_f, where k_b is the Boltzmann's constant, T is the temperature in kelvin and delta_f is the bandwidth
        #thermal_noise = constants.Boltzmann*293.15*list(NRbandwidth_prb_lookup[self.numerology][self.fr].keys())[list(NRbandwidth_prb_lookup[self.numerology][self.fr].values()).index(self.total_prb / (10 * 2**self.numerology))]*1000000*(self.compute_rbur()+0.001)
        thermal_noise = constants.Boltzmann*293.15*15*(2**self.numerology)*1000 # delta_F = 15*2^mu KHz each subcarrier since we are considering measurements at subcarrirer level (like RSRP)
        sinr = (10**(rsrp[self.bs_id]/10))/(thermal_noise + interference)
        
        r = self.prb_bandwidth_size*1000*math.log2(1+sinr) #bandwidth is in kHz
        #based on the numerology choosen and considered the frame duration of 10ms, we transmit 1ms for mu = 0, 0.5ms for mu = 1, 0.25ms for mu = 2, 0.125ms for mu = 3 for each PRB each 10ms
        #print(r)
        r = r / (10 * (2**self.numerology))
        #print(r)
        N_prb = math.ceil(data_rate*1000000 / r) #data rate is in Mbps
        return N_prb, r

    #this method will be called by an UE that tries to connect to this BS.
    #the return value will be the actual bandwidth assigned to the user
    def request_connection(self, ue_id, data_rate, rsrp):
        
        N_prb, r = self.compute_nprb_NR(data_rate, rsrp)
        old_N_prb = N_prb
        
        #check if there is enough bitrate, if not then do not allocate the user
        if self.total_bitrate - self.allocated_bitrate <= r*N_prb/1000000:
            return 0

        #check if there are enough PRBs
        if self.total_prb - self.allocated_prb <= N_prb:
            N_prb = self.total_prb - self.allocated_prb

        if ue_id not in self.ue_pb_allocation:
            self.ue_pb_allocation[ue_id] = N_prb
            self.allocated_prb += N_prb
        else:
            self.allocated_prb -= self.ue_pb_allocation[ue_id]
            self.ue_pb_allocation[ue_id] = N_prb
            self.allocated_prb += N_prb 

        if ue_id not in self.ue_bitrate_allocation:
            self.ue_bitrate_allocation[ue_id] = r * N_prb / 1000000  
            self.allocated_bitrate += r * N_prb / 1000000
        else:
            self.allocated_bitrate -= self.ue_bitrate_allocation[ue_id]
            self.ue_bitrate_allocation[ue_id] = r * N_prb / 1000000
            self.allocated_bitrate += r * N_prb / 1000000
        
        print("Allocated %s/%s NR PRB" %(N_prb, old_N_prb))    
        return r*N_prb/1000000 #we want a data rate in Mbps, not in bps

    def request_disconnection(self, ue_id):
        N_prb = self.ue_pb_allocation[ue_id]
        self.allocated_prb -= N_prb
        del self.ue_pb_allocation[ue_id]

    
    def update_connection(self, ue_id, data_rate, rsrp):

        N_prb, r = self.compute_nprb_NR(data_rate, rsrp)
        diff = N_prb - self.ue_pb_allocation[ue_id]

        #check before if there is enough bitrate
        if self.total_bitrate - self.allocated_bitrate < diff * r / 100000:
            return self.ue_pb_allocation[ue_id] * r / 1000000


        if self.total_prb - self.allocated_prb >= diff:
            #there is the place for more PRB allocation (or less if diff is negative)
            self.allocated_prb += diff
            self.ue_pb_allocation[ue_id] += diff

            self.allocated_bitrate += diff * r / 1000000
            self.ue_bitrate_allocation[ue_id] += diff * r / 1000000
        else:
            #there is no room for more PRB allocation
            diff = self.total_prb - self.allocated_prb
            self.allocated_prb += diff
            self.ue_pb_allocation[ue_id] += diff

            self.allocated_bitrate += diff * r / 1000000
            self.ue_bitrate_allocation[ue_id] += diff * r / 1000000
            
        N_prb = self.ue_pb_allocation[ue_id]
        return N_prb*r/1000000 #remember that we want the result in Mbps 

    #things to do before moving to the next timestep
    def next_timestep(self):
        #print(self.allocated_prb)
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
        self.position = (self.starting_position[0], self.starting_position[1])
        self.h_b = self.starting_position[2]

    def move(self, destination, speed):
        x_k = destination[0] - self.position[0]
        y_k = destination[1] - self.position[1]
        z_k = destination[2] - self.h_b
        theta_k = self.theta_k
        v_k = 1*(x_k*math.cos(theta_k) + y_k*math.sin(theta_k))
        v_z_k = 1*z_k
        if v_k > speed and v_k > 0:
            v_k = speed
        elif v_k < -speed and v_k < 0:
            v_k = -speed
        if v_z_k > speed and v_z_k > 0:
            v_z_k = speed
        elif v_z_k < -speed and v_z_k < 0:
            v_z_k = -speed
        w_k = 1*(math.atan2(-y_k,-x_k) - theta_k + math.pi)


        new_x = self.position[0]+v_k*math.cos(theta_k + (w_k / 2))
        new_y = self.position[1]+v_k*math.sin(theta_k + (w_k / 2))
        new_z = self.h_b + v_z_k
        new_theta = self.theta_k + w_k
        self.position = (new_x, new_y)
        self.h_b = new_z
        self.current_position = self.position
        self.theta_k = new_theta

    
    def compute_latency(self):
        return 0 #TODO

    