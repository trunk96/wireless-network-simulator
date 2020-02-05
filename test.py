import environment
import util

env = environment.wireless_environment(100000)
id = env.insert_ue(10)
env.place_base_station((100, 100, 40), 700, 180, 12, 20, 16, 3, 20)
env.place_base_station((200, 200, 40), 700, 180, 12, 20, 16, 3, 20)
#print(environment.compute_path_loss_cost_hata(env.ue_list[0], env.bs_list[0], env))
rsrp = env.discover_bs(id)
print(rsrp)
util.find_ue_by_id(0).connect_to_bs()
#for i in range (0, 100):
#    pos = env.ue_list[0].move()
#    print(pos)
#    rsrp = env.discover_bs(id)
#    print(rsrp)
