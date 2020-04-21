import environment
import math
from scipy import constants
import util

class DroneRelay:
    bs_type = "drone"

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
        return util.find_bs_by_id(self.linked_bs).reset()

    def move(self, destination, speed):
        x_k = destination[0] - self.position[0]
        y_k = destination[1] - self.position[1]
        theta_k = self.theta_k
        v_k = 1*(x_k*math.cos(theta_k) + y_k*math.sin(theta_k))
        if v_k > speed and v_k > 0:
            v_k = speed
        elif v_k < -speed and v_k < 0:
            v_k = -speed
        w_k = 1*(math.atan2(-y_k,-x_k) - theta_k + math.pi)


        new_x = self.position[0]+v_k*math.cos(theta_k + (w_k / 2))
        new_y = self.position[1]+v_k*math.sin(theta_k + (w_k / 2))
        new_theta = self.theta_k + w_k
        self.position = (new_x, new_y)
        self.current_position = self.position
        self.theta_k = new_theta
