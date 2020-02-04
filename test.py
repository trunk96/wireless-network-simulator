import environment

env = environment.wireless_environment(100000)
id = env.insert_ue(10)
env.place_base_station((0, 0, 40), 700, 180, 12, 20, 16, 3, 20)
env.place_base_station((500, 200, 40), 700, 180, 12, 20, 16, 3, 20)
#print(environment.compute_path_loss_cost_hata(env.ue_list[0], env.bs_list[0], env))
rsrp = env.discover_bs(id)
print(rsrp)
