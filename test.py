import environment
import util
import Satellite


env = environment.wireless_environment(100000)
id = env.insert_ue(100)
sat_id = env.place_SAT_base_station((1,1,1))
sat = util.find_bs_by_id(sat_id)
#print(util.compute_rsrp(util.find_ue_by_id(id), sat, env))
rsrp = env.discover_bs(id)
#print(rsrp)
util.find_ue_by_id(id).connect_to_bs()
#print(sat.ue_allocation)
#print(sat.frame_utilization)
util.find_ue_by_id(id).disconnect_from_bs()
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
