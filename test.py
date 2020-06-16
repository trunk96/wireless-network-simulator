import environment
import util
import Satellite
import numpy as np
import matplotlib.pyplot as plt
import random
import time
import os

PLOT = False
N_UE = 50

random.seed(2)


env = environment.wireless_environment(4000)
ue = []
bs = []

num = []
den = []

load_sat = []
load_relay = []
load_bs = []

connected_sat = []
connected_relay = []
connected_bs = []

'''
if not os.path.exists("scenario.npy"):
    #generate a scenario
    ue_directions = np.random.randint(0, high = 360, size = N_UE)
    ue_positions = []
    for i in range(0, N_UE):
        ue_positions.append((np.random.randint(0, high = env.x_limit+1), np.random.randint(0, high = env.y_limit+1), 1))
    np.save("scenario.npy", [ue_directions, ue_positions], allow_pickle=True)


scenario = np.load("scenario.npy", allow_pickle=True)   
'''

for i in range(0, N_UE):
    id = env.insert_ue(0, starting_position=(random.randint(0, env.x_limit-1), random.randint(0, env.y_limit-1), 1), speed = 10, direction = random.randint(0, 359))
    ue.append(id)

#sat_id = env.place_SAT_base_station((1,1,1))
#sat = util.find_bs_by_id(sat_id)
sat_bs = env.place_SAT_base_station((2000, 2000))
bs.append(sat_bs)

nr_bs2 = env.place_NR_base_station((5000, 1000, 40), 800, 2, 20, 16, 3, 100)
bs.append(nr_bs2)

#nr_bs3 = env.place_NR_base_station((4000, 1000, 40), 800, 2, 20, 16, 3, 100)
#bs.append(nr_bs3)

drone_bs1 = env.place_DRONE_relay((5000, 3000, 200), nr_bs2, 800, 80, 16, 3)
bs.append(drone_bs1)

drone_bs2 = env.place_DRONE_base_station((6500, 3000, 200), 800, 2, 15, 15, 1, 100)
bs.append(drone_bs2)
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
start_move = False
status = random.getstate()
#util.find_ue_by_id(0).disconnect_from_bs()
for cycle in range (0, 330):
    print("------------------------------------------------------CYCLE %s------------------------------------------------------" %cycle)
    random.shuffle(ue)
    num.append(0)
    den.append(0)
    sat = util.find_bs_by_id(0)
    load_sat.append(0)
    load_relay.append(0)
    load_bs.append(0)

    for j in range(0, len(ue)):
        print("\n\n")
        ue_j = util.find_ue_by_id(ue[j])
        ue_j.do_action(cycle)
        if ue_j.current_bs != None:
            num[cycle] += ue_j.actual_data_rate
            den[cycle] += 1
        if ue_j.current_bs == 0:
            load_sat[cycle] += ue_j.actual_data_rate
        elif ue_j.current_bs == 2:
            load_relay[cycle] += ue_j.actual_data_rate
        elif ue_j.current_bs == 3:
            load_bs[cycle] += ue_j.actual_data_rate        
        print("\n\n")
    '''
    t = util.find_bs_by_id(0).compute_rbur()
    load_sat.append(t*100)
    t = util.find_bs_by_id(2).compute_rbur()
    load_relay.append(t*100)
    t = util.find_bs_by_id(3).compute_rbur()
    load_bs.append(t*100)
    '''

    l = len(util.find_bs_by_id(0).get_connected_users())
    connected_sat.append(l)
    l = len(util.find_bs_by_id(2).get_connected_users())
    connected_relay.append(l)
    l = len(util.find_bs_by_id(3).get_connected_users())
    connected_bs.append(l)

    if sat.compute_rbur() > 0.2:
        start_move = True
    start_move = True ##
    if start_move:
        util.find_bs_by_id(bs[2]).move((3500, 1000, 150), 20)
        #util.find_bs_by_id(bs[2]).move((3500, 2000, 150), 20)
        util.find_bs_by_id(bs[3]).move((1000, 2000, 150), 20)
        #util.find_bs_by_id(bs[3]).move((2000, 500, 150), 20)

    if PLOT and cycle == 329:
        util.plot(ue, bs, env)
        plt.pause(0.1)
    env.next_timestep()

#plt.pause(15)

#res1 = [x/y for x, y in zip(num, den)]
res1 = []
for n in range(len(num)):
    if den[n] != 0:
        res1.append(num[n]/den[n])
    else:
        res1.append(None)

'''
start_move = False
random.setstate(status)
num = []
den = []
load_sat1 = []
load_bs1 = []
load_relay1 = []
connected_sat1 = []
connected_relay1 = []
connected_bs1 = []
env.reset(0)

for cycle in range (0, 330):
    print("------------------------------------------------------CYCLE %s------------------------------------------------------" %cycle)
    random.shuffle(ue)
    num.append(0)
    den.append(0)
    sat = util.find_bs_by_id(0)
    
    load_sat1.append(0)
    load_bs1.append(0)
    load_relay1.append(0)

    for j in range(0, len(ue)):
        print("\n\n")
        ue_j = util.find_ue_by_id(ue[j])
        ue_j.do_action(cycle)
        if ue_j.current_bs != None:
            num[cycle] += ue_j.actual_data_rate
            den[cycle] += 1
        if ue_j.current_bs == 0:
            load_sat1[cycle] += ue_j.actual_data_rate
        elif ue_j.current_bs == 2:
            load_relay1[cycle] += ue_j.actual_data_rate
        elif ue_j.current_bs == 3:
            load_bs1[cycle] += ue_j.actual_data_rate    
        print("\n\n")
    
    COMMENT HERE
    t = util.find_bs_by_id(0).compute_rbur()
    load_sat1.append(t*100)
    t = util.find_bs_by_id(2).compute_rbur()
    load_relay1.append(t*100)
    t = util.find_bs_by_id(3).compute_rbur()
    load_bs1.append(t*100)
    


    l = len(util.find_bs_by_id(0).get_connected_users())
    connected_sat1.append(l)
    l = len(util.find_bs_by_id(2).get_connected_users())
    connected_relay1.append(l)
    l = len(util.find_bs_by_id(3).get_connected_users())
    connected_bs1.append(l)

    if sat.compute_rbur() > 2: #impossible, so they never moves
        start_move = True
    if start_move:
        util.find_bs_by_id(bs[2]).move((3500, 1000, 150), 20)
        util.find_bs_by_id(bs[3]).move((1000, 2000, 150), 20)

    if PLOT:
        util.plot(ue, bs, env)
        plt.pause(0.1)
    env.next_timestep()

res2 = []
for n in range(len(num)):
    if den[n] != 0:
        res2.append(num[n]/den[n])
    else:
        res2.append(None)
#res2 = [x/y for x, y in zip(num, den)]
#print(res)
'''

fig, axs = plt.subplots(3)
#fig1, axs1 = plt.subplots(3)
axs[0].plot(load_sat, 'k')
axs[0].plot(load_relay, 'k-.')
axs[0].plot(load_bs, 'k--')
'''
axs1[0].plot(load_sat1, 'k')
axs1[0].plot(load_relay1, 'k-.')
axs1[0].plot(load_bs1, 'k--')
'''
axs[0].set_xlabel("Time (s)")
axs[0].set_ylabel("Load (Mbps)")
'''
axs1[0].set_xlabel("Time (s)")
axs1[0].set_ylabel("Load (Mbps)")
'''
'''
axs1[0].set_ylim(-10, max(load_sat1) + 50)
'''
axs[0].set_ylim(-10, max(load_sat) + 50)
#plt.tight_layout()

#fig, axs = plt.subplots()
axs[1].plot(connected_sat, 'k')
axs[1].plot(connected_relay, 'k-.')
axs[1].plot(connected_bs, 'k--')
'''
axs1[1].plot(connected_sat1, 'k')
axs1[1].plot(connected_relay1, 'k-.')
axs1[1].plot(connected_bs1, 'k--')
'''
axs[1].set_xlabel("Time (s)")
axs[1].set_ylabel("Connected UEs")
axs[1].set_ylim(-1, 51)
'''
axs1[1].set_xlabel("Time (s)")
axs1[1].set_ylabel("Connected UEs")
axs1[1].set_ylim(-1, 51)
#plt.tight_layout()
'''
#fig, ax = plt.subplots()
axs[2].plot(res1, 'k')
axs[2].set_xlabel("Time (s)")
axs[2].set_ylabel("Bitrate (Mbps)")
axs[2].set_ylim(5, 11)

'''
axs1[2].plot(res2, 'k')
axs1[2].set_xlabel("Time (s)")
axs1[2].set_ylabel("Bitrate (Mbps)")
axs1[2].set_ylim(5, 11)
'''
plt.tight_layout()
plt.show()

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
