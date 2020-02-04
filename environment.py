import ue
import bs
import util
from concurrent.futures import ThreadPoolExecutor
import math


class wireless_environment:
    bs_list = []
    ue_list = []
    thermal_noise = 0
    x_limit = None
    y_limit = None
    env_type = util.EnvType.URBAN

    def __init__(self, n, m = None):
        if m is not None:
            self.y_limit = m
        else:
            self.y_limit = n
        self.x_limit = n
    
    def insert_ue(self, requested_bitrate, starting_position = None):
        if starting_position is not None and (starting_position[2] > 10 or starting_position[2] < 1):
            raise Exception("COST-HATA model requires UE height in [1,10]m")
        
        ue_id = -1
        
        if None in self.ue_list:
            ue_id = self.ue_list.index(None)
        else:
            ue_id = len(self.ue_list)
        
        if starting_position is None:
            new_ue = ue.user_equipment(requested_bitrate, ue_id, (0,0,1), self)
        else: 
            new_ue = ue.user_equipment(requested_bitrate, ue_id, starting_position, self)
        self.ue_list.append(new_ue)
        return new_ue.ue_id
    

    def remove_ue(self, ue_id):
        self.ue_list[ue_id] = None

    def place_base_station(self, position, carrier_frequency, pbr_bandwidth, number_subcarriers, antenna_power, antenna_gain, feeder_loss, available_bandwidth = None, total_pbr = None):
        if position[2] > 200 or position[2] < 30:
            raise Exception("COST-HATA model requires BS height in [30, 200]m")
        
        if (carrier_frequency < 150 or carrier_frequency > 2000):
            raise Exception("your results may be incorrect because your carrier frequency is outside the boundaries of COST-HATA path loss model")
        if (available_bandwidth is None and total_pbr is None):
            raise Exception("you havce to specify available bandwidth or total PBRs")
        elif (total_pbr is not None):
            new_bs = bs.base_station(len(self.bs_list), total_pbr, pbr_bandwidth, number_subcarriers, antenna_power, antenna_gain, feeder_loss, carrier_frequency, position)
        else:
            if (available_bandwidth in util.bandwidth_pbr_lookup):
                new_bs = bs.base_station(len(self.bs_list), util.bandwidth_pbr_lookup[available_bandwidth], pbr_bandwidth, number_subcarriers, antenna_power, antenna_gain, feeder_loss, carrier_frequency, position)
            else:
                raise Exception("if you indicate the available bandwidth, it must be 1.4, 3, 5, 10, 15 or 20 MHz")
        
        self.bs_list.append(new_bs)
        return new_bs.bs_id
    
    #this method shall be called by an UE 
    #that wants to have a measure of the RSRP 
    #associated to each BS
    def discover_bs(self, ue_id):
       thread_pool = []
       rsrp = [None]*len(self.bs_list)
       with ThreadPoolExecutor(max_workers=len(self.bs_list)) as executor:
            for i in range(0, len(self.bs_list)):
                thread = executor.submit(util.compute_rsrp, self.ue_list[ue_id], self.bs_list[i], self)
                thread_pool.append(thread)
            for i in range(0, len(self.bs_list)):
                rsrp[i] = thread_pool[i].result()
       return rsrp

