import random
import util
import math
#import matlab.engine

MAX_STEP = 2000

# service classes for UEs, "class: Mbps"
ue_class = {
    0: 30,
    1: 15
}
ue_class_lambda = {
    0: 1/20,
    1: 1/15
}

class user_equipment:
    MATLAB = 0
    RANDOM = 0
    epsilon = -1

    def __init__ (self, requested_bitrate, service_class, ue_id, starting_position, env, speed, direction):
        self.ue_id = ue_id
        self.requested_bitrate = requested_bitrate
        self.current_position = (starting_position[0], starting_position[1])
        self.starting_position = (starting_position[0], starting_position[1])
        self.h_m = starting_position[2]
        self.env = env
        self.speed = speed #how much distance we made in one step
        self.direction = direction #in degrees from the x axis (0 horizontal movement, 90 vertical movement)
        self.old_position = (starting_position[0], starting_position[1])
        self.old_sevice_class = service_class
        self.service_class = service_class
        self.lambda_exp = ue_class_lambda[self.service_class]
        self.current_bs = None
        self.actual_data_rate = 0
        self.last_action_t = 0
        

    
    def move(self):
        if self.RANDOM == 1:
            return self.random_move()
        else:
            return self.line_move()

    def random_move(self):
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

    def line_move(self):
        new_x = self.current_position[0]+self.speed*math.cos(math.radians(self.direction))
        new_y = self.current_position[1]+self.speed*math.sin(math.radians(self.direction))
        
        #90-degrees bumping
        if new_x <= 0 and new_y <= 0:
            #bottom-left corner
            new_x = 0
            new_y = 0
            self.direction -= 180
        elif new_x <= 0 and new_y >= self.env.y_limit:
            #top-left corener
            new_x = 0
            new_y = self.env.y_limit
            self.direction += 180
        elif new_x >= self.env.x_limit and new_y >= self.env.y_limit:
            #top-right corner
            new_x = self.env.x_limit
            new_y = self.env.y_limit
            self.direction += 180
        elif new_x >= self.env.x_limit and new_y <= 0:
            #bottom-right corner
            new_x = self.env.x_limit
            new_y = 0
            self.direction -= 180
        elif new_x >= self.env.x_limit and self.direction != 90 and self.direction != 270:
            #bumping on the right margin
            new_x = self.env.x_limit
            if self.direction < 90 and self.direction > 0:
                self.direction += 90
            elif self.direction > 270 and self.direction < 360:
                self.direction -= 90
        elif new_x <= 0 and self.direction != 90 and self.direction != 270:
            #bumping on the left margin
            new_x = 0
            if self.direction > 180 and self.direction < 270:
                self.direction += 90
            elif self.direction > 90 and self.direction < 180:
                self.direction -= 90
        elif new_y <= 0 and self.direction != 0 and self.direction != 180:
            #bumping on the bottom margin
            new_y = 0
            self.direction = (360 - self.direction) % 360
        elif new_y >= self.env.y_limit and self.direction != 0 and self.direction != 180:
            #bumping on the top margin
            new_y = self.env.y_limit
            self.direction = (360 - self.direction) % 360

        self.direction = self.direction % 360
        self.current_position = (new_x, new_y)
        return self.current_position

    def do_action(self, t):
        if self.current_bs == None:
            self.connect_to_bs()
            return
        # compute the time spent in the service class
        delta_t = 0# t - self.last_action_t
        # compute probability of change action
        prob = 1 - (1 - math.exp(-self.lambda_exp * delta_t))
        if random.random() > prob:
            # it's time to change service class
            print("CHANGED SERVICE CLASS: User ID %s has now changed to class %s" %(self.ue_id, self.service_class))
            self.disconnect_from_bs()
            if self.service_class == 0:
                self.service_class = 1
            else:
                self.service_class = 0
            # apply new class parameters: requested bitrate, lambda, last action time
            self.requested_bitrate = ue_class[self.service_class]
            self.lambda_exp = ue_class_lambda[self.service_class]
            self.last_action_t = t
            self.connect_to_bs()
        else:
            self.update_connection()

    def connect_to_bs_random(self):
        available_bs = self.env.discover_bs(self.ue_id)
        if len(available_bs) == 0:
            print("[NO BASE STATION FOUND]: User ID %s has not found any base station" %(self.ue_id))
            return
        elif len(available_bs) == 1:
            #this means there is only one available bs, so we have to connect to it
            #bs = list(available_bs.keys())[0]
            #self.actual_data_rate = util.find_bs_by_id(bs).request_connection(self.ue_id, self.requested_bitrate, available_bs)   
            self.current_bs , self.actual_data_rate = self.env.request_connection(self.ue_id, self.requested_bitrate, available_bs)

        else:
            if self.MATLAB == 1:
                #import function from matlab, in order to select the best action

                #eng = matlab.engine.start_matlab()
                #ret = eng.nomefunzione(arg1, arg2,...,argn)
                return
            else:
                bs, rsrp = random.choice(list(available_bs.items()))
                self.actual_data_rate = util.find_bs_by_id(bs).request_connection(self.ue_id, self.requested_bitrate, available_bs)
                #self.current_bs, self.actual_data_rate = self.env.request_connection(self.ue_id, self.requested_bitrate, available_bs)
                self.current_bs = bs
        print("[CONNECTION_ESTABLISHED]: User ID %s is now connected to base_station %s with a data rate of %s/%s Mbps" %(self.ue_id, self.current_bs, self.actual_data_rate, self.requested_bitrate))
    
    def connect_to_bs(self):
        available_bs = self.env.discover_bs(self.ue_id)
        if len(available_bs) == 0:
            print("[NO BASE STATION FOUND]: User ID %s has not found any base station" %(self.ue_id))
            return
        elif len(available_bs) == 1:
            #this means there is only one available bs, so we have to connect to it
            #bs = list(available_bs.keys())[0]
            #self.actual_data_rate = util.find_bs_by_id(bs).request_connection(self.ue_id, self.requested_bitrate, available_bs)   
            self.current_bs , self.actual_data_rate = self.env.request_connection(self.ue_id, self.requested_bitrate, available_bs)

        else:
            if self.MATLAB == 1:
                #import function from matlab, in order to select the best action

                #eng = matlab.engine.start_matlab()
                #ret = eng.nomefunzione(arg1, arg2,...,argn)
                return
            else:
                #bs = max(available_bs, key = available_bs.get)
                #self.actual_data_rate = util.find_bs_by_id(bs).request_connection(self.ue_id, self.requested_bitrate, available_bs)
                self.current_bs, self.actual_data_rate = self.env.request_connection(self.ue_id, self.requested_bitrate, available_bs)
                #self.current_bs = bs
        print("[CONNECTION_ESTABLISHED]: User ID %s is now connected to base_station %s with a data rate of %s/%s Mbps" %(self.ue_id, self.current_bs, self.actual_data_rate, self.requested_bitrate))


    def disconnect_from_bs(self):
        if self.current_bs != None:
            util.find_bs_by_id(self.current_bs).request_disconnection(self.ue_id)
            print("[CONNECTION_TERMINATED]: User ID %s is now disconnected from base_station %s" %(self.ue_id, self.current_bs))
            self.current_bs = None
            #self.actual_data_rate = 0
        return
        

    
    def update_connection(self):
        if self.current_bs == None:
            self.connect_to_bs()
            return

        available_bs = self.env.discover_bs(self.ue_id)
        #print(available_bs)
        if len(available_bs) == 0:
            print("[NO BASE STATION FOUND]: User ID %s has not found any base station during connection update" %(self.ue_id))
        elif self.current_bs in available_bs:
            self.actual_data_rate = util.find_bs_by_id(self.current_bs).update_connection(self.ue_id, self.requested_bitrate, available_bs)
            if self.actual_data_rate < self.requested_bitrate:
                print("[POOR BASE STATION]: User ID %s has a poor connection to its base station (actual data rate is %s/%s Mbps)" %(self.ue_id, self.actual_data_rate, self.requested_bitrate))
                self.disconnect_from_bs()
                self.connect_to_bs()
            '''
            elif random.random() < self.epsilon:
                print("[RANDOM DISCONNECTION]: User ID %s was randomly disconnected from its base station (actual data rate is %s/%s Mbps)" %(self.ue_id, self.actual_data_rate, self.requested_bitrate))
                self.disconnect_from_bs()
                self.connect_to_bs()
            '''
        else:
            #in this case the current base station is no more visible
            print("[BASE STATION LOST]: User ID %s has not found its base station during connection update" %(self.ue_id))
            self.disconnect_from_bs()
            self.connect_to_bs()

        print("[CONNECTION_UPDATE]: User ID %s has updated its connection to base_station %s with a data rate of %s/%s Mbps" %(self.ue_id, self.current_bs, self.actual_data_rate, self.requested_bitrate))

    def next_timestep(self):
        self.old_position = self.current_position
        self.move()

    def reset(self, t):
        self.disconnect_from_bs()
        self.current_position = self.starting_position
        self.service_class = self.old_sevice_class
        self.lambda_exp = ue_class_lambda[self.service_class]
        self.requested_bitrate = ue_class[self.service_class]
        self.last_action_t = t

        

    
