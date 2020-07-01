import UserEquipment as ue
import LTEBaseStation as LTEbs
import NRBaseStation as NRbs
import Satellite as SATbs
import Drone as DRONEbs
import util
from concurrent.futures import ThreadPoolExecutor
import math
import random


class wireless_environment:
    bs_list = []
    ue_list = []
    x_limit = None
    y_limit = None
    env_type = util.EnvType.URBAN

    def __init__(self, n, m = None, sampling_time = 1):
        if m is not None:
            self.y_limit = m
        else:
            self.y_limit = n
        self.x_limit = n
        self.cumulative_reward = 0
        self.sampling_time = sampling_time
        self.wardrop_epsilon = 0.5 #TODO
        self.wardrop_beta = 0
    
    def insert_ue(self, ue_class, starting_position = None, speed = 0, direction = 0):
        if starting_position is not None and (starting_position[2] > 10 or starting_position[2] < 1):
            raise Exception("COST-HATA model requires UE height in [1,10]m")
        elif ue_class not in ue.ue_class:
            raise Exception("Invalid service class for the UE, available service classes are: %s" %(ue.ue_class.keys()))
        ue_id = -1
        
        if None in self.ue_list:
            ue_id = self.ue_list.index(None)
        else:
            ue_id = len(self.ue_list)
        
        if starting_position is None:
            new_ue = ue.user_equipment(ue.ue_class[ue_class], ue_class, ue_id, (random.randint(0, self.x_limit),random.randint(0, self.y_limit),1), self, speed*self.sampling_time, direction)
        else: 
            new_ue = ue.user_equipment(ue.ue_class[ue_class], ue_class, ue_id, starting_position, self, speed*self.sampling_time, direction)
        
        if (ue_id == len(self.ue_list)):
            self.ue_list.append(new_ue)
        else:
            self.ue_list[ue_id] = new_ue
        return new_ue.ue_id
    

    def remove_ue(self, ue_id):
        self.ue_list[ue_id] = None

    
    def place_SAT_base_station(self, total_bitrate, position):       
        new_bs = SATbs.Satellite(len(self.bs_list), total_bitrate, position, self)
        
        self.bs_list.append(new_bs)
        return new_bs.bs_id

    def place_LTE_base_station(self, position, carrier_frequency, antenna_power, antenna_gain, feeder_loss, available_bandwidth, total_bitrate):
        
        if (available_bandwidth in LTEbs.LTEbandwidth_prb_lookup):
            #  LTE standard defines 12 subcarriers of 15KHz each, so the pbr_bandwidth is 180KHz
            #  LTEbandwidth_prb_lookup defines the number of blocks of 180KHz available in the specified bandwidth,
            #  so we have to multiply by the number of time slots (sub-frames in LTE terminology) in a time frame
            new_bs = LTEbs.LTEBaseStation(len(self.bs_list), LTEbs.LTEbandwidth_prb_lookup[available_bandwidth] * 10, 180, 12, antenna_power, antenna_gain, feeder_loss, carrier_frequency, total_bitrate, position, self)
        else:
            raise Exception("if you indicate the available bandwidth, it must be 1.4, 3, 5, 10, 15 or 20 MHz")
        
        self.bs_list.append(new_bs)
        return new_bs.bs_id
    
    def place_NR_base_station(self, position, carrier_frequency, numerology, antenna_power, antenna_gain, feeder_loss, available_bandwidth, total_bitrate = 0, drone = False):
        #check if the bandwith is in line with the specified numerology and specified carrier frequency
        fr = -1
        if (carrier_frequency <= 6000):  #below 6GHz
            fr = 0
        elif (carrier_frequency >= 24250 and carrier_frequency <= 52600): #between 24.25GHz and 52.6GHz
            fr = 1
        else:
            raise Exception("NR frequency outside admissible ranges")

        if available_bandwidth in NRbs.NRbandwidth_prb_lookup[numerology][fr]:
            prb_size = 15*(2**numerology)*12 #15KHz*12subcarriers for numerology 0, 30KHz*12subcarriers for numerology 1, etc.
            #  NRbandwidth_prb_lookup defines the number of blocks of 180KHz available in the specified bandwidth with a certain numerology,
            #  so we have to multiply by the number of time slots (sub-frames in LTE terminology) in a time frame
            if drone == False:
                new_bs = NRbs.NRBaseStation(len(self.bs_list), NRbs.NRbandwidth_prb_lookup[numerology][fr][available_bandwidth] * (10 * 2**numerology), prb_size, 12, numerology, antenna_power, antenna_gain, feeder_loss, carrier_frequency, total_bitrate, position, self)
            else:
                new_bs = DRONEbs.DroneBaseStation(len(self.bs_list), DRONEbs.NRbandwidth_prb_lookup[numerology][fr][available_bandwidth] * (10 * 2**numerology), prb_size, 12, numerology, antenna_power, antenna_gain, feeder_loss, carrier_frequency, total_bitrate, position, self)
        else:
            raise Exception("The choosen bandwidth is not present in 5G NR standard with such numerology and frequency range")

        self.bs_list.append(new_bs)
        return new_bs.bs_id

    def place_DRONE_relay(self, starting_position, linked_bs_id, carrier_frequency, amplification_factor, antenna_gain, feeder_loss):
        new_bs = DRONEbs.DroneRelay(len(self.bs_list), linked_bs_id, amplification_factor, antenna_gain, feeder_loss, carrier_frequency, starting_position, self)
        self.bs_list.append(new_bs)
        return new_bs.bs_id

    def place_DRONE_base_station(self, position, carrier_frequency, numerology, antenna_power, antenna_gain, feeder_loss, available_bandwidth, total_bitrate):
        return self.place_NR_base_station(position, carrier_frequency, numerology, antenna_power, antenna_gain, feeder_loss, available_bandwidth, total_bitrate, drone = True)
    
    #this method shall be called by an UE 
    #that wants to have a measure of the RSRP 
    #associated to each BS
    def discover_bs(self, ue_id):
       thread_pool = []
       #rsrp = [None]*len(self.bs_list)
       rsrp = dict()
       with ThreadPoolExecutor(max_workers=len(self.bs_list)) as executor:
            for i in range(0, len(self.bs_list)):
                thread = executor.submit(util.compute_rsrp, self.ue_list[ue_id], self.bs_list[i], self)
                thread_pool.append(thread)
            for i in range(0, len(self.bs_list)):
                res = thread_pool[i].result() 
                #if res > -1000000:
                if (res > util.MIN_RSRP):
                    rsrp[i] = res
       #print(rsrp)
       return rsrp

    def initial_timestep(self):
        #compute beta value:
        #beta, by definition, is max{1/r}, where r is the data rate of a single resource block (or symbol) seen by a certain UE
        self.wardrop_beta = 0
        for ue in self.ue_list:
            rsrp = self.discover_bs(ue.ue_id)
            for elem in rsrp:
               r = util.find_bs_by_id(elem).compute_r(ue.ue_id, rsrp)
               if util.find_bs_by_id(elem).wardrop_alpha/(r/1000000) > self.wardrop_beta: #we convert r in Mbps
                   self.wardrop_beta =  util.find_bs_by_id(elem).wardrop_alpha/(r/1000000)
        #now call each initial_timestep function in order to set the initial conditions for each commodity in terms of bitrate
        #to be requested to each BS
        for ue in self.ue_list:
            ue.initial_timestep()
        return

    def next_timestep(self):
        #with ThreadPoolExecutor(max_workers=len(self.ue_list)) as executor:
        if self.wardrop_epsilon > self.wardrop_beta*ue.ue_class[0]*len(self.ue_list):
            print("Warning: Epsilon is outside the admissible ranges (", self.wardrop_epsilon, "/", self.wardrop_beta*ue.ue_class[0]*len(self.ue_list), ")")
        for ues in self.ue_list:
            #thread = executor.submit()
            ues.next_timestep()
        for bss in self.bs_list:
            bss.next_timestep()

    
    def request_connection(self, ue_id, requested_bitrate, available_bs):

        bs = max(available_bs, key = available_bs.get)
        data_rate = util.find_bs_by_id(bs).request_connection(ue_id, requested_bitrate, available_bs)
        reward = self.compute_reward(None, bs, data_rate, requested_bitrate, available_bs, ue_id)
        self.cumulative_reward += reward
        return bs, data_rate
       
    def compute_reward(self, state, action, bitrate, desired_data_rate, rsrp, ue_id):
        if action in rsrp:
            allocated, total = util.find_bs_by_id(action).get_connection_info(ue_id)
            alpha = 0
            if util.find_ue_by_id(ue_id).service_class == 0:
                alpha = 3
            else:
                alpha = 1
            if bitrate > desired_data_rate:
                # in case the DQN made a correct allocation I do not want the user occupies too much resources, so if the allocated resources
                # for the users are too much I will discount the reward of a proportional value
                return alpha * desired_data_rate / (allocated/total)
            else:
                if allocated > 0:
                    # in case of a bad allocation, I do not want again that the user occupies too much resources (better if it is allocated to
                    # one of its neighbor base stations)
                    return alpha * (desired_data_rate**2) * (bitrate - desired_data_rate) #* (allocated/total) * 100
                else:
                    return alpha * (desired_data_rate**2) * (bitrate - desired_data_rate)
        else:
            # it should never go here (there are checks on actions in the argmax)
            return -10000

    def reset(self, cycle):
        for ue in self.ue_list:
            ue.reset(cycle)
        for bs in self.bs_list:
            bs.reset()
