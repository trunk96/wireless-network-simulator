import environment
import math


#Table 5.3.3-1: Minimum guardband [kHz] (FR1) and Table: 5.3.3-2: Minimum guardband [kHz] (FR2), 3GPPP 38.104
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



class NRBaseStation:
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

    def __init__(self, bs_id, total_prb, prb_bandwidth_size, number_subcarriers, numerology, antenna_power, antenna_gain, feeder_loss, carrier_frequency, position, env):
        if position[2] > 200 or position[2] < 30:
            raise Exception("COST-HATA model requires BS height in [30, 200]m")
        
        if (carrier_frequency < 150 or carrier_frequency > 2000):
            raise Exception("your results may be incorrect because your carrier frequency is outside the boundaries of COST-HATA path loss model")
        
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