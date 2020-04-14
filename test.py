import environment
import util
import Satellite
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import random
import time


PLOT = False

if PLOT:
    plt.ion()
    fig, ax = plt.subplots()
run = 0
plot1 = []
plot2 = []
ann1 = []
ann2 = []



def plot(ue, bs):
    global run
    global ax
    global fig
    global plot1
    global plot2
    global ann1
    global ann2
    if len(plot1) != 0 and len(plot2) != 0 and len(ann1) != 0 and len(ann2) != 0:
        x = np.array([])
        x = np.reshape(x, (-1, 2))
        for elem in plot1:
            elem.set_offsets(x)
        for elem in plot2:
            elem.set_offsets(x)
        for a in ann1:
            try:
                a.remove()
            except:
                continue
        for a in ann2:
            try:
                a.remove()
            except:
                continue
    
    x_ue = []
    y_ue = []
    x_bs = []
    y_bs = []

    ax.set_xlim(0, env.x_limit)
    ax.set_ylim(0, env.y_limit)
    colors = cm.rainbow(np.linspace(0, 1, len(bs)))

    for j in bs:
        x_bs.append(util.find_bs_by_id(j).position[0])
        y_bs.append(util.find_bs_by_id(j).position[1])

    for i in range(0, len(ue)):
        x_ue.append(util.find_ue_by_id(ue[i]).current_position[0])
        y_ue.append(util.find_ue_by_id(ue[i]).current_position[1])

    for i in range(0, len(ue)):
        for j in range(0, len(bs)):
            if util.find_ue_by_id(ue[i]).current_bs == j:
                plot1.append(ax.scatter(x_ue[i], y_ue[i], color = colors[j]))
                break
        else:
            plot1.append(ax.scatter(x_ue[i], y_ue[i], color = "tab:grey"))

    for i in range(0, len(ue)):
        a = ax.annotate(str(ue[i]), (x_ue[i], y_ue[i]))
        ann1.append(a)

    for j in range(0, len(bs)):
        plot2.append(ax.scatter(x_bs[j], y_bs[j], color = colors[j], label = "BS", marker = "s", s = 400))
    
    for j in range(0, len(bs)):
        a = ax.annotate("BS"+str(j), (x_bs[j], y_bs[j]))
        ann2.append(a)

    ax.grid(True)
    fig.canvas.draw()


def plot_old(ue, bs):
    global run
    global ax
    global fig
    global plot1
    global plot2
    global ann1
    global ann2
    if plot1 != None and plot2 != None and len(ann1) != 0 and len(ann2) != 0:
        x = np.array([])
        x = np.reshape(x, (-1, 2))
        plot1.set_offsets(x.copy())
        plot2.set_offsets(x.copy())
        for a in ann1:
            try:
                a.remove()
            except:
                continue
        for a in ann2:
            try:
                a.remove()
            except:
                continue
    x = []
    y = []
    x1 =[]
    y1 = []
    for i in range(0, len(ue)):
        x.append(util.find_ue_by_id(ue[i]).current_position[0])
        y.append(util.find_ue_by_id(ue[i]).current_position[1])

    for j in bs:
        x1.append(util.find_bs_by_id(j).position[0])
        y1.append(util.find_bs_by_id(j).position[1])


    ax.set_xlim(0, env.x_limit)
    ax.set_ylim(0, env.y_limit)
    plot1 = ax.scatter(x, y, color = "tab:blue", label = "UE")
    for i in range(0, len(ue)):
        a = ax.annotate(str(ue[i]), (x[i], y[i]))
        ann1.append(a)

    plot2 = ax.scatter(x1, y1, color = "tab:orange", label = "BS")
    for j in bs:
        a = ax.annotate("BS"+str(j), (x1[j], y1[j]))
        ann2.append(a)

    if run == 0:
        ax.legend()
        run += 1
    ax.grid(True)
    fig.canvas.draw()


env = environment.wireless_environment(1000)
ue = []
bs = []
for i in range(0, 50):
    id = env.insert_ue(10, speed = 10, direction = random.randint(0, 359))
    ue.append(id)

#sat_id = env.place_SAT_base_station((1,1,1))
#sat = util.find_bs_by_id(sat_id)
nr_bs = env.place_NR_base_station((200, 200, 40), 800, 2, 20, 16, 3, 100)
bs.append(nr_bs)

nr_bs1 = env.place_NR_base_station((800, 200, 40), 800, 2, 20, 16, 3, 100)
bs.append(nr_bs1)

nr_bs2 = env.place_NR_base_station((500, 800, 40), 800, 2, 20, 16, 3, 100)
bs.append(nr_bs2)

lte_bs = env.place_LTE_base_station((50, 500, 40), 700, 20, 16, 3, 20)
bs.append(lte_bs)

lte_bs1 = env.place_LTE_base_station((900, 900, 40), 700, 20, 16, 3, 20)
bs.append(lte_bs1)

sat = env.place_SAT_base_station((500, 500, 35800000))
bs.append(sat)


if PLOT:
    plot(ue, bs)
    plt.pause(0.1)
#time.sleep(1)
#print(util.compute_rsrp(util.find_ue_by_id(id), sat, env))
random.shuffle(ue)
for j in ue:
    util.find_ue_by_id(j).connect_to_bs()

if PLOT:
    plot(ue, bs)
    plt.pause(0.1)
#time.sleep(1)
env.next_timestep()

#util.find_ue_by_id(0).disconnect_from_bs()
for cycle in range (0, 1000):
    print("------------------------------------------------------CYCLE %s------------------------------------------------------" %cycle)
    random.shuffle(ue)
    for j in ue:
        print("\n\n")
        util.find_ue_by_id(j).update_connection()
        print("\n\n")

    if PLOT:
        plot(ue, bs)
        plt.pause(0.1)
    #time.sleep(1)
    env.next_timestep()



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
