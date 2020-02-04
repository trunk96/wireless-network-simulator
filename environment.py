import ue
import bs
from concurrent.futures import ThreadPoolExecutor
import math
from enum import Enum


class EnvType (Enum):
    RURAL = 0
    SUBURBAN = 1
    URBAN = 2

bandwidth_pbr_lookup = {
    1.4: 6,
    3: 15,
    5: 25,
    10: 50,
    15: 75,
    20: 100
}

class wireless_environment:
    bs_list = []
    ue_list = []
    thermal_noise = 0
    x_limit = None
    y_limit = None
    env_type = EnvType.URBAN

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
            new_ue = ue.user_equipment(requested_bitrate, ue_id, (0,0,1))
        else: 
            new_ue = ue.user_equipment(requested_bitrate, ue_id, starting_position)
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
            if (available_bandwidth in bandwidth_pbr_lookup):
                new_bs = bs.base_station(len(self.bs_list), bandwidth_pbr_lookup[available_bandwidth], pbr_bandwidth, number_subcarriers, antenna_power, antenna_gain, feeder_loss, carrier_frequency, position)
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
                thread = executor.submit(compute_rsrp, self.ue_list[ue_id], self.bs_list[i], self)
                thread_pool.append(thread)
            for i in range(0, len(self.bs_list)):
                rsrp[i] = thread_pool[i].result()
       return rsrp




def compute_rsrp(ue, bs, env):
    path_loss = compute_path_loss_cost_hata(ue, bs, env)
    subcarrier_power = 10*math.log10(bs.antenna_power*1000 / (bs.total_pbr*bs.number_subcarriers))
    return subcarrier_power + bs.antenna_gain - bs.feeder_loss - path_loss

def compute_path_loss_cost_hata(ue, bs, env, save = None):
    #compute distance first
    dist = math.sqrt((ue.current_position[0]-bs.position[0])**2 + (ue.current_position[1]-bs.position[1])**2)
    #compute C_0, C_f, b(h_b), a(h_m) and C_m with the magic numbers defined by the model
    if bs.carrier_frequency <= 1500 and bs.carrier_frequency >= 150 :
        C_0 = 69.55
        C_f = 26.16
        b = 13.82*math.log10(bs.h_b)
        if env.env_type == EnvType.URBAN:
            C_m = 0
        elif env.env_type == EnvType.SUBURBAN:
            C_m = -2*((math.log10(bs.carrier_frequency/28))**2) - 5.4
        else:
            C_m = -4.78*((math.log10(bs.carrier_frequency))**2) + 18.33*math.log10(bs.carrier_frequency) - 40.94
    else:  
        C_0 = 46.3
        C_f = 26.16
        b = 13.82*math.log10(bs.h_b)
        if env.env_type == EnvType.URBAN:
            C_m = 3
        elif env.env_type == EnvType.SUBURBAN:
            C_m = 0
        else:
            raise Exception("COST-HATA model is not defined for frequencies in 1500-2000MHz with RURAL environments")
    
    if env.env_type == EnvType.SUBURBAN or env.env_type == EnvType.RURAL:
        a = (1.1*math.log10(bs.carrier_frequency) - 0.7)*ue.h_m - 1.56*math.log10(bs.carrier_frequency) + 0.8
    else:
        if bs.carrier_frequency >= 150 and bs.carrier_frequency <= 300:
            a = 8.29*(math.log10(1.54*ue.h_m)**2) - 1.1
        else:
            a = 3.2*(math.log10(11.75*ue.h_m)**2) - 4.97
    
    path_loss = C_0 + C_f * math.log10(bs.carrier_frequency) - b - a + (44.9-6.55*math.log10(bs.h_b))*math.log10(dist/1000) + C_m
    if (save is not None):
        save = path_loss
    return path_loss
