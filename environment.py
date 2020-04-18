import UserEquipment as ue
import LTEBaseStation as LTEbs
import NRBaseStation as NRbs
import Satellite as SATbs
import dqn
import util
from concurrent.futures import ThreadPoolExecutor
import math
import random
import numpy as np
import time




class wireless_environment:
    bs_list = []
    ue_list = []
    x_limit = None
    y_limit = None
    env_type = util.EnvType.URBAN

    #this instance variable will be used just to compute next_state vector for DQN
    next_ue = None
    #this instance variable will be used just for indentify training and testing
    training = False

    def __init__(self, training, n, m = None):
        if m is not None:
            self.y_limit = m
        else:
            self.y_limit = n
        self.x_limit = n
        self.training = training
        self.cumulative_reward = 0
    
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
            new_ue = ue.user_equipment(ue.ue_class[ue_class], ue_class, ue_id, (random.randint(0, self.x_limit),random.randint(0, self.y_limit),1), self, speed, direction)
        else: 
            new_ue = ue.user_equipment(ue.ue_class[ue_class], ue_class, ue_id, starting_position, self, speed, direction)
        
        if (ue_id == len(self.ue_list)):
            self.ue_list.append(new_ue)
        else:
            self.ue_list[ue_id] = new_ue
        return new_ue.ue_id
    

    def remove_ue(self, ue_id):
        self.ue_list[ue_id] = None

    
    def place_SAT_base_station(self, position):       
        new_bs = SATbs.Satellite(len(self.bs_list), position, self)
        
        self.bs_list.append(new_bs)
        return new_bs.bs_id

    def place_LTE_base_station(self, position, carrier_frequency, antenna_power, antenna_gain, feeder_loss, available_bandwidth):
        
        if (available_bandwidth in LTEbs.LTEbandwidth_prb_lookup):
            #  LTE standard defines 12 subcarriers of 15KHz each, so the pbr_bandwidth is 180KHz
            #  LTEbandwidth_prb_lookup defines the number of blocks of 180KHz available in the specified bandwidth,
            #  so we have to multiply by the number of time slots (sub-frames in LTE terminoloty) in a time frame
            new_bs = LTEbs.LTEBaseStation(len(self.bs_list), LTEbs.LTEbandwidth_prb_lookup[available_bandwidth]*10, 180, 12, antenna_power, antenna_gain, feeder_loss, carrier_frequency, position, self)
        else:
            raise Exception("if you indicate the available bandwidth, it must be 1.4, 3, 5, 10, 15 or 20 MHz")
        
        self.bs_list.append(new_bs)
        return new_bs.bs_id
    
    def place_NR_base_station(self, position, carrier_frequency, numerology, antenna_power, antenna_gain, feeder_loss, available_bandwidth):
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
            #  so we have to multiply by the number of time slots (sub-frames in LTE terminoloty) in a time frame
            new_bs = NRbs.NRBaseStation(len(self.bs_list), NRbs.NRbandwidth_prb_lookup[numerology][fr][available_bandwidth] * (10 * 2**numerology), prb_size, 12, numerology, antenna_power, antenna_gain, feeder_loss, carrier_frequency, position, self)
        else:
            raise Exception("The choosen bandwidth is not present in 5G NR standard with such numerology and frequency range")

        self.bs_list.append(new_bs)
        return new_bs.bs_id



    
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
                if (res > util.MIN_RSRP):
                    rsrp[i] = res
       return rsrp


    def setup_dqn(self):
        if self.training:
            self.dqn_engine = dqn.DQN(self, tau = 0.05)
        else:
            self.dqn_engine = dqn.DQN(self, epsilon = 0, epsilon_min = 0, epsilon_decay = 0)
            self.dqn_engine.load_model("models\\model.h5")
    
    def request_connection(self, ue_id, data_rate, rsrp):
        # here a connection request from user ue_id arrives. We have to interrogate the DQN in order 
        # to find the correct BS the user have to connect
        
        state = [-1.0] * (len(self.bs_list) * 2 + 2)
        for elem in rsrp:
            t, r = util.find_bs_by_id(elem).get_state()
            state[elem] = r/t
        
        for i in range(len(self.bs_list), len(self.bs_list)*2):
            if i - len(self.bs_list) in rsrp:
                state[i] = (rsrp[i-len(self.bs_list)] + 140)/140

        state[len(self.bs_list)*2] = util.find_ue_by_id(ue_id).actual_data_rate 
        state[len(self.bs_list)*2 + 1] = util.find_ue_by_id(ue_id).service_class

        print([state[0:len(self.bs_list)], state[len(self.bs_list):len(self.bs_list)*2], state[len(self.bs_list*2)], state[len(self.bs_list)*2 + 1]])

        state = np.array(state)
        state = np.reshape(state, (-1, len(self.bs_list)*2+2))

        action = self.dqn_engine.act(state, rsrp)  
        print("ACTION SELECTED BY DQN: %s" %(action))

        bitrate = util.find_bs_by_id(action).request_connection(ue_id, data_rate, rsrp)
        reward = self.compute_reward(state, action, bitrate, data_rate, rsrp, ue_id)
        print("REWARD RECEIVED BY DQN: %s" %(reward))
        self.cumulative_reward += reward

        if self.training:
            # new state is composed by updated base station occupation level, by following UE's rsrps, by following UE's actual bitrate and by following UE's service class 
            new_state = state.copy()
            t, a = util.find_bs_by_id(action).get_state()
            new_state[0][action] = a/t

            next_ue = util.find_ue_by_id(self.next_ue)
            next_ue_rsrp = self.discover_bs(next_ue.ue_id)
            for i in range (len(self.bs_list), len(self.bs_list)*2):
                if i - len(self.bs_list) in next_ue_rsrp:
                    new_state[0][i] = (next_ue_rsrp[i - len(self.bs_list)] + 140)/140
            if next_ue.current_bs in next_ue_rsrp:
                new_state[0][len(self.bs_list)*2] = util.find_bs_by_id(next_ue.current_bs).update_connection(next_ue.ue_id, next_ue.requested_bitrate, next_ue_rsrp)
            else:
                #both in case the current base station is no more visibile and in the case
                #no base station is visible to next_ue, then the next bitrate will be 0 for this moment
                new_state[0][len(self.bs_list)*2] = 0

            new_state[0][len(self.bs_list)*2 + 1] = next_ue.service_class
            #print("ID %s, new_state = %s" %(self.next_ue, new_state[0]))

            self.dqn_engine.remember(state.copy(), action, reward, new_state.copy(), False)
            self.dqn_engine.replay()
            self.dqn_engine.target_train()



        return action, bitrate

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

    def next_timestep(self):
        '''
        in case we want to use threads...

        with ThreadPoolExecutor(max_workers=len(self.ue_list)) as executor:
            for ue in self.ue_list:
                thread = executor.submit(ue.next_timestep())
        '''

        for ue in self.ue_list:
            ue.next_timestep()
        for bs in self.bs_list:
            bs.next_timestep()

    def reset(self, cycle):
        for ue in self.ue_list:
            ue.reset(cycle)
        for bs in self.bs_list:
            bs.reset()
        

