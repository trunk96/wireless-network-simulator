import environment
import util
import Satellite
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import random
import time
import os


PLOT = True
N_UE = 100

random.seed(1)

env = environment.wireless_environment(False, 10000/2)
ue = []
bs = []

if not os.path.exists("scenario.npy"):
    #generate a scenario
    ue_directions = np.random.randint(0, high = 360, size = N_UE)
    ue_positions = []
    for i in range(0, N_UE):
        ue_positions.append((np.random.randint(0, high = env.x_limit+1), np.random.randint(0, high = env.y_limit+1), 1))
    np.save("scenario.npy", [ue_directions, ue_positions], allow_pickle=True)


scenario = np.load("scenario.npy", allow_pickle=True)   

for i in range(0, N_UE):
    if i < 50:
        id = env.insert_ue(0, starting_position=scenario[1][i], speed = 10, direction = scenario[0][i])
    else:
        id = env.insert_ue(1, starting_position=scenario[1][i], speed = 10, direction = scenario[0][i])

    ue.append(id)

#sat_id = env.place_SAT_base_station((1,1,1))
#sat = util.find_bs_by_id(sat_id)
nr_bs = env.place_NR_base_station((2000, 2000, 40), 800, 2, 20, 16, 3, 100)
bs.append(nr_bs)

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
env.setup_dqn()

print(env.dqn_engine.model.summary())

num = 0
den = 0


if PLOT:
    util.plot(ue, bs, env)
    plt.pause(0.1)
#time.sleep(1)
#print(util.compute_rsrp(util.find_ue_by_id(id), sat, env))
'''
random.shuffle(ue)
for j in range(0, len(ue)):
    if j <= len(ue) - 2:
            env.next_ue = ue[j+1]
    else:
        env.next_ue = ue[j]
    ue_j = util.find_ue_by_id(ue[j])
    ue_j.connect_to_bs_random()

    #update statistics
    num_j = ue_j.actual_data_rate/ue_j.requested_bitrate
    if ue_j.service_class == 0:
        num_j *= 3
        den += 3
    else:
        den += 1
    num += num_j
'''

if PLOT:
    util.plot(ue, bs, env)
    plt.pause(0.1)
#time.sleep(1)
env.next_timestep()


#util.find_ue_by_id(0).disconnect_from_bs()
for cycle in range (0, 30):
    print("------------------------------------------------------CYCLE %s------------------------------------------------------" %cycle)
    random.shuffle(ue)
    for j in range(0, len(ue)):
        print("\n\n")
        if j <= len(ue) - 2:
            env.next_ue = ue[j+1]
        else:
            env.next_ue = ue[j]
        ue_j = util.find_ue_by_id(ue[j])
        ue_j.do_action(cycle)
        
        #update statistics
        num_j = ue_j.actual_data_rate/ue_j.requested_bitrate
        if ue_j.service_class == 0:
            num_j *= 3
            den += 3
        else:
            den += 1
        num += num_j

        print("\n\n")

    if PLOT:
        util.plot(ue, bs, env)
        plt.pause(0.1)
    #time.sleep(1)
    env.next_timestep()

print(num/den)
print(env.cumulative_reward)


time.sleep(1)

