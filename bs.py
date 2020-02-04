class base_station:
    pbr_bandwidth_size = 0
    total_pbr = 0
    allocated_pbr = 0
    ue_pb_allocation = {}
    antenna_gain = 0
    feeder_loss = 0
    antenna_power = 0
    bs_id = 0
    carrier_frequency = 0 #in MHz 
    position = None
    h_b = 40 #height of BS antenna
    number_subcarriers = 0

    def __init__(self, bs_id, total_pbr, pbr_bandwidth_size, number_subcarriers, antenna_power, antenna_gain, feeder_loss, carrier_frequency, position):
        self.pbr_bandwidth_size = pbr_bandwidth_size
        self.total_pbr = total_pbr
        self.antenna_power = antenna_power
        self.antenna_gain = antenna_gain
        self.feeder_loss = feeder_loss
        self.bs_id = bs_id
        self.carrier_frequency = carrier_frequency
        self.position = (position[0],position[1])
        self.h_b = position[2]
        self.number_subcarriers = number_subcarriers

    
    

