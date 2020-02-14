import random
import util
#import matlab.engine

MAX_STEP = 20

class user_equipment:
    requested_bitrate = 0
    ue_id = None
    current_position = None
    h_m = 1 #height of UE antenna
    env = None
    current_bs = None
    actual_data_rate = 0
    MATLAB = 0

    def __init__ (self, requested_bitrate, ue_id, starting_position, env):
        self.ue_id = ue_id
        self.requested_bitrate = requested_bitrate
        self.current_position = (starting_position[0], starting_position[1])
        self.h_m = starting_position[2]
        self.env = env

    def move(self):
        val = random.randint(1, 4)
        size = random.randint(0, MAX_STEP) 
        if val == 1: 
            if (self.current_position[0] + size) > 0 and (self.current_position[0] + size) < self.env.x_limit:
                self.current_position = (self.current_position[0] + size, self.current_position[1])
        elif val == 2: 
            if (self.current_position[0] - size) > 0 and (self.current_position[0] - size) < self.env.x_limit:
                self.current_position = (self.current_position[0] - size, self.current_position[1])
        elif val == 3: 
            if (self.current_position[1] + size) > 0 and (self.current_position[1] + size) < self.env.y_limit:
                self.current_position = (self.current_position[0], self.current_position[1] + size)
        else: 
            if (self.current_position[1] - size) > 0 and (self.current_position[1] - size) < self.env.y_limit:
                self.current_position = (self.current_position[0], self.current_position[1] - size)
        return self.current_position
    
    def connect_to_bs(self):
        available_bs = self.env.discover_bs(self.ue_id)
        if len(available_bs) == 1:
            #this means there is only one available bs, so we have to connect to it
            bs = list(available_bs.keys())[0]
            self.actual_data_rate = util.find_bs_by_id(bs).request_connection(self.ue_id, self.requested_bitrate, available_bs)   
            self.current_bs = bs
        else:
            if self.MATLAB == 1:
                #import function from matlab, in order to select the best action

                #eng = matlab.engine.start_matlab()
                #ret = eng.nomefunzione(arg1, arg2,...,argn)
                return
            else:
                bs = max(available_bs, key = available_bs.get)
                self.actual_data_rate = util.find_bs_by_id(bs).request_connection(self.ue_id, self.requested_bitrate, available_bs)
                self.current_bs = bs
                print(bs)


    def disconnect_from_bs(self):
        util.find_bs_by_id(self.current_bs).request_disconnection(self.ue_id)

    def next_timestep(self):
        self.move()

    
