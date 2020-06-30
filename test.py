import environment
import util
import Satellite
import numpy as np
import matplotlib.pyplot as plt
import random
import time
import os

PLOT = False
N_UE = 5
ITER = 10000 

SELECTED_UE = 3

random.seed(2)


env = environment.wireless_environment(4000, sampling_time=0.001)
ue = []
bs = []
error = []
latency = []

for i in range(0, N_UE):
    id = env.insert_ue(0, starting_position=(random.randint(0, env.x_limit-1), random.randint(0, env.y_limit-1), 1), speed = 0, direction = random.randint(0, 359))
    #id = env.insert_ue(0, starting_position=(0, 0, 1), speed = 0, direction = random.randint(0, 359))
    ue.append(id)

sat_bs = env.place_SAT_base_station(10000, (2000, 2000))
bs.append(sat_bs)

#nr_bs2 = env.place_NR_base_station((1500, 1500, 40), 800, 2, 20, 16, 3, 100, total_bitrate = 10000)

parm = [
    #BS1
    {"pos": (1500, 1500, 40),
    "freq": 800,
    "numerology": 1, 
    "power": 20,
    "gain": 16,
    "loss": 3,
    "bandwidth": 20,
    "max_bitrate": 100},
    
    #BS2
    {"pos": (3000, 3000, 40),
    "freq": 800,
    "numerology": 1, 
    "power": 20,
    "gain": 16,
    "loss": 3,
    "bandwidth": 20,
    "max_bitrate": 100},

    #BS3
    {"pos": (1000, 500, 40),
    "freq": 1700,
    "numerology": 1, 
    "power": 1,
    "gain": 5,
    "loss": 1,
    "bandwidth": 40,
    #15
    "max_bitrate": 100},

    #BS4
    {"pos": (2000, 500, 40),
    "freq": 1700,
    "numerology": 1, 
    "power": 1,
    "gain": 5,
    "loss": 1,
    "bandwidth": 40,
    "max_bitrate": 100},

    #BS5
    {"pos": (500, 1500, 40),
    "freq": 1700,
    "numerology": 1, 
    "power": 1,
    "gain": 5,
    "loss": 1,
    "bandwidth": 40,
    "max_bitrate": 100},

    #BS6
    {"pos": (2500, 1500, 40),
    "freq": 1700,
    "numerology": 1, 
    "power": 1,
    "gain": 5,
    "loss": 1,
    "bandwidth": 40,
    "max_bitrate": 100},

    #BS7
    {"pos": (1000, 2500, 40),
    "freq": 1700,
    "numerology": 1, 
    "power": 1,
    "gain": 5,
    "loss": 1,
    "bandwidth": 40,
    "max_bitrate": 100},

    #BS8
    {"pos": (2000, 2500, 40),
    "freq": 1700,
    "numerology": 1, 
    "power": 1,
    "gain": 5,
    "loss": 1,
    "bandwidth": 40,
    "max_bitrate": 100},

    #BS9
    {"pos": (2500, 2000, 40),
    "freq": 1700,
    "numerology": 1, 
    "power": 1,
    "gain": 5,
    "loss": 1,
    "bandwidth": 40,
    "max_bitrate": 100},

    #BS10
    {"pos": (3500, 2000, 40),
    "freq": 1700,
    "numerology": 1, 
    "power": 1,
    "gain": 5,
    "loss": 1,
    "bandwidth": 40,
    "max_bitrate": 20},

    #BS11
    {"pos": (2000, 3000, 40),
    "freq": 1700,
    "numerology": 1, 
    "power": 1,
    "gain": 5,
    "loss": 1,
    "bandwidth": 40,
    "max_bitrate": 100},

    #BS12
    {"pos": (4000, 3000, 40),
    "freq": 1700,
    "numerology": 1, 
    "power": 1,
    "gain": 5,
    "loss": 1,
    "bandwidth": 40,
    "max_bitrate": 100},

    #BS13
    {"pos": (2500, 4000, 40),
    "freq": 1700,
    "numerology": 1, 
    "power": 1,
    "gain": 5,
    "loss": 1,
    "bandwidth": 40,
    "max_bitrate": 100},

    #BS14
    {"pos": (3500, 4000, 40),
    "freq": 1700,
    "numerology": 1, 
    "power": 1,
    "gain": 5,
    "loss": 1,
    "bandwidth": 40,
    "max_bitrate": 100}

]

for i in range(14):
    nr_bs2 = env.place_NR_base_station(parm[i]["pos"], parm[i]["freq"], parm[i]["numerology"], parm[i]["power"], parm[i]["gain"], parm[i]["loss"], parm[i]["bandwidth"], total_bitrate = parm[i]["max_bitrate"])
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

phone1 = util.find_ue_by_id(0)
#phone2 = util.find_ue_by_id(1)
#print(phone.bs_bitrate_allocation)

#util.plot(ue, bs, env)
#plt.pause(10)

for phone in ue:
    util.find_ue_by_id(phone).connect_to_all_bs()
#phone2.connect_to_bs_id(1)
#phone2.connect_to_bs_id(0)
env.next_timestep()
#print(phone.bs_bitrate_allocation)

for i in range(0,ITER):
    if i % 100 == 0:
        print(i)
        
        #print(util.find_bs_by_id(2).get_state())
        #print(util.find_bs_by_id(2).allocated_bitrate)
        #print(util.find_bs_by_id(2).ue_bitrate_allocation)
        print("BITRATE: ", util.find_ue_by_id(SELECTED_UE).bs_bitrate_allocation)
        print("ACTUAL BITRATE: ", util.find_ue_by_id(SELECTED_UE).current_bs)
        if(i!= 0):
            print("LATENCY: ", latency[i-1])
        prb_dict = {}
        for elem in util.find_ue_by_id(SELECTED_UE).bs_bitrate_allocation:
            if util.find_bs_by_id(elem).bs_type != "sat" and SELECTED_UE in util.find_bs_by_id(elem).ue_pb_allocation:
                prb_dict[elem] = util.find_bs_by_id(elem).ue_pb_allocation[SELECTED_UE]
            elif util.find_bs_by_id(elem).bs_type == "sat" and SELECTED_UE in util.find_bs_by_id(elem).ue_allocation:
                prb_dict[elem] = util.find_bs_by_id(elem).ue_allocation[SELECTED_UE]/64
        print("PRB: ",prb_dict)
        #print(util.find_bs_by_id(2).ue_pb_allocation[SELECTED_UE])
        
    max_e = 0
    for phone in ue:
        #print(phone)
        util.find_ue_by_id(phone).update_connection()
    #phone2.update_connection()
        l_max = 0
        l_min = float("inf")
        latency_phone={}
        for bs in util.find_ue_by_id(phone).bs_bitrate_allocation:
            l = util.find_bs_by_id(bs).compute_latency(phone)
            if (phone == SELECTED_UE):
                latency_phone[bs]=l
            if util.find_ue_by_id(phone).bs_bitrate_allocation[bs] > 0.0001 and l > l_max:
                l_max = l
            elif util.find_ue_by_id(phone).bs_bitrate_allocation[bs] < util.find_bs_by_id(bs).total_bitrate-(env.wardrop_epsilon/(2*env.wardrop_beta)) and l < l_min:
                l_min = l
        e = l_max - l_min
        if e > max_e:
            max_e = e
        if phone == SELECTED_UE:
            latency.append(latency_phone)
    error.append(max_e)

    env.next_timestep()
    #print(phone1.bs_bitrate_allocation)

print("\n\n---------------------------------------------------\n\n")
for phone in ue:
    print("UE %s: %s" %(phone, util.find_ue_by_id(phone).bs_bitrate_allocation))
print("\n\n---------------------------------------------------\n\n")
#print(latency)
print(util.find_ue_by_id(3).current_position)
l_2 = []
l_0 = []
l_1 = []
l_10 = []



for elem in latency:
    l_2.append(elem[2])
    l_1.append(elem[1]) 
    l_0.append(elem[0])
    l_10.append(elem[10])

#print(l_2)
import matplotlib.pyplot as plt
x = range(ITER)
y = []
y.append(l_2)
y.append(l_1)
y.append(l_0)
y.append(l_10)

plt.xlabel("X-axis")
plt.ylabel("Y-axis")
plt.title("A test graph")
for i in range(len(y)):
    plt.plot(x,y[i],label = 'id %s'%i)
plt.legend()
plt.show()
#print(phone1.current_position)
#print(phone2.bs_bitrate_allocation)
#print(phone2.current_position)'''