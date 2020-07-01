import environment
import util
import Satellite
import numpy as np
import matplotlib.pyplot as plt
import random
import time
import os
import pandas as pd

PLOT = False
N_UE = 20
ITER = 40000    

SELECTED_UE = 3

random.seed(2)


env = environment.wireless_environment(4000, sampling_time=0.001)
ue = []
bs = []
error = []
latency = {}
prbs = {}
bitrates = {}

for i in range(0, N_UE):
    id = env.insert_ue(0, starting_position=(random.randint(0, env.x_limit-1), random.randint(0, env.y_limit-1), 1), speed = 0, direction = random.randint(0, 359))
    #id = env.insert_ue(0, starting_position=(0, 0, 1), speed = 0, direction = random.randint(0, 359))
    ue.append(id)

sat_bs = env.place_SAT_base_station(10000, (1000, 2000))
bs.append(sat_bs)

#nr_bs2 = env.place_NR_base_station((1500, 1500, 40), 800, 2, 20, 16, 3, 100, total_bitrate = 10000)

parm = [
    #BS1
    {"pos": (2000, 2000, 40),
    "freq": 800,
    "numerology": 1, 
    "power": 20,
    "gain": 16,
    "loss": 3,
    "bandwidth": 20,
    "max_bitrate": 1000},
    
    #BS2
    {"pos": (1000, 1000, 40),
    "freq": 1700,
    "numerology": 1, 
    "power": 1,
    "gain": 5,
    "loss": 1,
    "bandwidth": 40,
    "max_bitrate": 1000},

    #BS3
    {"pos": (2000, 500, 40),
    "freq": 1900,
    "numerology": 1, 
    "power": 1,
    "gain": 5,
    "loss": 1,
    "bandwidth": 40,
    #15
    "max_bitrate": 1000},

    #BS4
    {"pos": (3000, 1000, 40),
    "freq": 2000,
    "numerology": 1, 
    "power": 1,
    "gain": 5,
    "loss": 1,
    "bandwidth": 25,
    "max_bitrate": 55},

    #BS5
    {"pos": (3000, 3000, 40),
    "freq": 1700,
    "numerology": 1, 
    "power": 1,
    "gain": 5,
    "loss": 1,
    "bandwidth": 40,
    "max_bitrate": 1000},

    #BS6
    {"pos": (2000, 3500, 40),
    "freq": 1900,
    "numerology": 1, 
    "power": 1,
    "gain": 5,
    "loss": 1,
    "bandwidth": 40,
    "max_bitrate": 1000},

    #BS7
    {"pos": (1000, 3000, 40),
    "freq": 2000,
    "numerology": 1, 
    "power": 1,
    "gain": 5,
    "loss": 1,
    "bandwidth": 25,
    "max_bitrate": 1000}
]

for i in range(len(parm)):
    nr_bs2 = env.place_NR_base_station(parm[i]["pos"], parm[i]["freq"], parm[i]["numerology"], parm[i]["power"], parm[i]["gain"], parm[i]["loss"], parm[i]["bandwidth"], total_bitrate = parm[i]["max_bitrate"])
    bs.append(nr_bs2)



env.initial_timestep();
print(env.wardrop_beta)

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
        print("-------------------", i, "-------------------")
        
        #print(util.find_bs_by_id(2).get_state())
        #print(util.find_bs_by_id(2).allocated_bitrate)
        #print(util.find_bs_by_id(2).ue_bitrate_allocation)
        '''
        print("BITRATE: ", util.find_ue_by_id(SELECTED_UE).bs_bitrate_allocation)
        print("ACTUAL BITRATE: ", util.find_ue_by_id(SELECTED_UE).current_bs)
        rsrp = env.discover_bs(SELECTED_UE)
        sinr = {}
        for bsc in rsrp:
            sinr[bsc] = util.find_bs_by_id(bsc).compute_sinr(rsrp)
        print("SINR: ", sinr)
        if(i!= 0):
            print("LATENCY: ", latency[SELECTED_UE][i-1])
        prb_dict = {}
        for elem in util.find_ue_by_id(SELECTED_UE).bs_bitrate_allocation:
            if util.find_bs_by_id(elem).bs_type != "sat" and SELECTED_UE in util.find_bs_by_id(elem).ue_pb_allocation:
                prb_dict[elem] = util.find_bs_by_id(elem).ue_pb_allocation[SELECTED_UE]
            elif util.find_bs_by_id(elem).bs_type == "sat" and SELECTED_UE in util.find_bs_by_id(elem).ue_allocation:
                prb_dict[elem] = util.find_bs_by_id(elem).ue_allocation[SELECTED_UE]/64
        print("PRB: ",prb_dict)
        '''
        if i != 0:
            for elem in ue:
                phonex = util.find_ue_by_id(elem)
                for bsx in phonex.current_bs:
                    if phonex.current_bs[bsx] < phonex.bs_bitrate_allocation[bsx]:
                        print("Warning: UE", elem, "has saturated BS ", bsx)
        #print(util.find_bs_by_id(2).ue_pb_allocation[SELECTED_UE])
        
        for bsi in bs:
            if util.find_bs_by_id(bsi).bs_type != "sat":
                print("BS ", bsi, " PRB: ", util.find_bs_by_id(bsi).allocated_prb, "/", util.find_bs_by_id(bsi).total_prb, " Bitrate: ", util.find_bs_by_id(bsi).allocated_bitrate, "/", util.find_bs_by_id(bsi).total_bitrate)
            else:
                print("BS ", bsi, " PRB: ", util.find_bs_by_id(bsi).frame_utilization/64, "/", util.find_bs_by_id(bsi).total_symbols/64, " Bitrate: ", util.find_bs_by_id(bsi).allocated_bitrate, "/", util.find_bs_by_id(bsi).total_bitrate)
        
    max_e = 0
    for phone in ue:
        #print(phone)
        util.find_ue_by_id(phone).update_connection()
    #phone2.update_connection()
        l_max = 0
        l_min = float("inf")
        latency_phone={}
        for bsa in util.find_ue_by_id(phone).bs_bitrate_allocation:
            l = util.find_bs_by_id(bsa).compute_latency(phone)
            
            latency_phone[bsa]=l

            if util.find_ue_by_id(phone).bs_bitrate_allocation[bsa] > 0.0001 and l > l_max:
                l_max = l
            elif util.find_ue_by_id(phone).bs_bitrate_allocation[bsa] < util.find_bs_by_id(bsa).total_bitrate-(env.wardrop_epsilon/(2*env.wardrop_beta)) and l < l_min:
                l_min = l
        e = l_max - l_min
        if e > max_e:
            max_e = e
        if phone not in latency:
            latency[phone] = []
        latency[phone].append(latency_phone)
    error.append(max_e)

    for bsi in bs:
        if bsi not in prbs:
            prbs[bsi] = []
        if bsi not in bitrates:
            bitrates[bsi] = []
        
        if util.find_bs_by_id(bsi).bs_type != "sat":
            prbs[bsi].append(util.find_bs_by_id(bsi).allocated_prb)
            bitrates[bsi].append(util.find_bs_by_id(bsi).allocated_bitrate)
        else:
            prbs[bsi].append(util.find_bs_by_id(bsi).frame_utilization/64)
            bitrates[bsi].append(util.find_bs_by_id(bsi).allocated_bitrate)
              

    env.next_timestep()
    #print(phone1.bs_bitrate_allocation)

print("\n\n---------------------------------------------------\n\n")
for phone in ue:
    print("UE %s: %s" %(phone, util.find_ue_by_id(phone).bs_bitrate_allocation))
print("\n\n---------------------------------------------------\n\n")
#print(latency)
print(util.find_ue_by_id(3).current_position)

ue_latency = {}

for phone in latency:
    df = pd.DataFrame.from_dict(latency[phone])
    df.to_csv(".\\data\\latency_UE"+str(phone)+".csv", sep=";")

df = pd.DataFrame(error)
df.to_csv(".\\data\\error.csv", sep=";")

for bsi in bs:
    df = pd.DataFrame.from_dict(prbs[bsi])
    df.to_csv(".\\data\\resourceblocks_BS"+str(bsi)+".csv", sep=";")
    df = pd.DataFrame.from_dict(bitrates[bsi])
    df.to_csv(".\\data\\bitrate_BS"+str(bsi)+".csv", sep=";")

'''
x = range(ITER)

plt.xlabel("Simulation time (ms)")
plt.ylabel("Error")
plt.title("Error")
plt.plot(x,error)
plt.show()
'''
'''
for phone in ue:

    latency_dict = {}
    for elem in latency[phone]:
        for bsx in elem:
            if bsx not in latency_dict:
                latency_dict[bsx] = []
            latency_dict[bsx].append(elem[bsx])

    #print(l_2)

    x = range(ITER)

    plt.xlabel("Simulation time (ms)")
    plt.ylabel("Latency")
    plt.title("Latency for UE " + str(phone))
    for i in latency_dict:
        plt.plot(x,latency_dict[i],label = 'id %s'%i)
    plt.legend()
    plt.show()
#print(phone1.current_position)
#print(phone2.bs_bitrate_allocation)
#print(phone2.current_position)
'''