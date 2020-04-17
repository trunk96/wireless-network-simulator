import environment
import util

env = environment.wireless_environment(False, 10000)

id = env.insert_ue(0, starting_position=(3000, 3000, 1), speed = 10, direction = 190)
lte = env.place_LTE_base_station((50, 50, 40), 700, 20, 16, 3, 20)
#nr = env.place_NR_base_station((50, 50, 40), 800, 2, 20, 16, 3, 100)
#sat = env.place_SAT_base_station((500, 500, 35800000))

rsrp = env.discover_bs(id)
print(rsrp)

bs = util.find_bs_by_id(nr)
#bs = util.find_bs_by_id(lte)
#bs = util.find_bs_by_id(sat)
bs.request_connection(id, 10, rsrp)

print(bs.get_connected_users())
print(bs.get_state())