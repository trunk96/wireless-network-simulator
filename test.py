import environment
import util
import Satellite
import numpy as np
import matplotlib.pyplot as plt
import random
import time
import os

PLOT = False
N_UE = 1

random.seed(2)


env = environment.wireless_environment(4000, sampling_time=0.001)
ue = []
bs = []

for i in range(0, N_UE):
    #id = env.insert_ue(0, starting_position=(random.randint(0, env.x_limit-1), random.randint(0, env.y_limit-1), 1), speed = 0, direction = random.randint(0, 359))
    id = env.insert_ue(0, starting_position=(0, 0, 1), speed = 0, direction = random.randint(0, 359))
    ue.append(id)

sat_bs = env.place_SAT_base_station(10000, (2000, 2000))
bs.append(sat_bs)

#nr_bs2 = env.place_NR_base_station((1500, 1500, 40), 800, 2, 20, 16, 3, 100, total_bitrate = 10000)
nr_bs2 = env.place_NR_base_station((1500, 1500, 40), 800, 1, 20, 16, 3, 20, total_bitrate = 10000)
bs.append(nr_bs2)

#lte_bs = env.place_LTE_base_station((500, 500, 40), 700, 20, 16, 3, 20, total_bitrate = 10000)
#bs.append(lte_bs)

#nr_bs3 = env.place_NR_base_station((4000, 1000, 40), 800, 2, 20, 16, 3, 100)
#bs.append(nr_bs3)

#drone_bs1 = env.place_DRONE_relay((5000, 3000, 200), nr_bs2, 800, 80, 16, 3)
#bs.append(drone_bs1)

#drone_bs2 = env.place_DRONE_base_station((6500, 3000, 200), 800, 2, 15, 15, 1, 100)
#bs.append(drone_bs2)
'''
nr_bs1 = env.place_NR_base_station((8000, 2000, 40), 800, 2, 20, 16, 3, 100)
bs.append(nr_bs1)

nr_bs2 = env.place_NR_base_station((5000, 8000, 40), 800, 2, 20, 16, 3, 100)
bs.append(nr_bs2)

lte_bs = env.place_LTE_base_station((500, 5000, 40), 700, 20, 16, 3, 20)
bs.append(lte_bs)

lte_bs1 = env.place_LTE_base_station((9000, 9000, 40), 700, 20, 16, 3, 20)
bs.append(lte_bs1)

sat = env.place_SAT_base_station((5000, 5000, 35800000))
bs.append(sat)
'''
env.initial_timestep();
print(env.wardrop_beta)

phone = util.find_ue_by_id(0)
print(phone.bs_bitrate_allocation)

phone.connect_to_bs_id(1)
phone.connect_to_bs_id(0)
env.next_timestep()
print(phone.bs_bitrate_allocation)

for i in range(0,100000):
    phone.update_connection()
    env.next_timestep()
    print(phone.bs_bitrate_allocation)