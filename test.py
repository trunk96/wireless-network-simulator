import environment
import util
import Satellite
import numpy as np
import matplotlib.pyplot as plt
import random
import time
import os

PLOT = True
N_UE = 100

random.seed(1)

env = environment.wireless_environment(10000/2)
ue = []
bs = []

num = 0
den = 0

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


if PLOT:
    util.plot(ue, bs, env)
    plt.pause(0.1)
#time.sleep(1)
#print(util.compute_rsrp(util.find_ue_by_id(id), sat, env))
'''
random.shuffle(ue)
for j in ue:
    util.find_ue_by_id(j).connect_to_bs()


if PLOT:
    util.plot(ue, bs, env)
    #plt.pause(0.1)
#time.sleep(1)
env.next_timestep()
'''

#util.find_ue_by_id(0).disconnect_from_bs()
for cycle in range (0, 50):
    print("------------------------------------------------------CYCLE %s------------------------------------------------------" %cycle)
    random.shuffle(ue)
    for j in range(0, len(ue)):
        print("\n\n")
        ue_j = util.find_ue_by_id(ue[j])
        ue_j.do_action(cycle)
        num_j = ue_j.actual_data_rate/ue_j.requested_bitrate
        if ue_j.service_class == 0:
            num_j *= 3
            den += 3
        else:
            den += 1
            #num_j = 0
        num += num_j


        print("\n\n")

    if PLOT:
        util.plot(ue, bs, env)
        plt.pause(0.1)
    #time.sleep(1)
    env.next_timestep()

print(num/den)
print(env.cumulative_reward)

#util.find_ue_by_id(id).update_connection()
#print(sat.ue_allocation)
#print(sat.frame_utilization)
#util.find_ue_by_id(id).disconnect_from_bs()
#print(sat.ue_allocation)
#print(sat.frame_utilization)

'''
from satellite import satellite

env = environment.wireless_environment(100000)
id = env.insert_ue(10)
env.place_NR_base_station((100, 100, 40), 800, 2, 20, 16, 3, 100)
#env.place_LTE_base_station((100, 100, 40), 700, 20, 16, 3, 20)
#print(environment.compute_path_loss_cost_hata(env.ue_list[0], env.bs_list[0], env))
rsrp = env.discover_bs(id)
print(rsrp)
util.find_ue_by_id(0).connect_to_bs()

pos = env.ue_list[0].move()

util.find_ue_by_id(0).update_connection()
#for i in range (0, 100):
#    pos = env.ue_list[0].move()
#    print(pos)
#    rsrp = env.discover_bs(id)
#    print(rsrp)


#sat = satellite((100,20,1e6),BRmax=50,BRocc=40,BRreq=10,freq=20, antenna_gain=43, antenna_power=31, subcarrier_power=30)
#fspl = sat.fspl_dB()
#print(fspl)
#eirp = sat.eirp()
#print(eirp)
#bit = sat.received_power()
#print(bit)

import matplotlib.pyplot as plt
import numpy as np
import time

env = environment.wireless_environment(100000)
id = env.insert_ue(10, starting_position = (4000, 80000, 1), speed = 10000, direction = 27)

plt.ion()

fig, ax = plt.subplots()

plot = ax.scatter([], [])
ax.set_xlim(0, 100000)
ax.set_ylim(0, 100000)

while True:
    # get two gaussian random numbers, mean=0, std=1, 2 numbers
    point = util.find_ue_by_id(0).move()
    point = [point[0], point[1]]
    print(point)
    
    #point = np.asarray(point)
    # get the current points as numpy array with shape  (N, 2)
    array = plot.get_offsets()
    array = np.reshape(array, (-1,2))
    point = np.reshape(point, (-1,2))
    

    # add the points to the plot
    array = np.concatenate((array, point))
    #print(array)
    plot.set_offsets(array)

    # update x and ylim to show all points:
    #ax.set_xlim(array[:, 0].min() - 0.5, array[:,0].max() + 0.5)
    #ax.set_ylim(array[:, 1].min() - 0.5, array[:, 1].max() + 0.5)
    # update the figure
    fig.canvas.draw()
    time.sleep(1)
'''
