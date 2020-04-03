import environment
import util
from satellite import satellite

env = environment.wireless_environment(100000)
id = env.insert_ue(10)
env.place_LTE_base_station((100, 100, 40), 700, 20, 16, 3, 20)
env.place_LTE_base_station((20000, 20000, 40), 700, 20, 16, 3, 20)
#print(environment.compute_path_loss_cost_hata(env.ue_list[0], env.bs_list[0], env))
rsrp = env.discover_bs(id)
print(rsrp)
util.find_ue_by_id(0).connect_to_bs()
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