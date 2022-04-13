# 4G/5G/Satellite Wireless Network Simulator

**<ins>New version of the simulator available here: https://github.com/trunk96/wireless-network-simulator-v2</ins>**

This tool is designed in the context of my PhD in Automatic Control in Sapienza University of Rome to simulate resource allocations in 4G, 5G and Satellite networks, without entering in the details of the various protocols and of the syncronization mechanisms. Moreover this simulator does not considers actual transmission of the data, but just allocation of uplink/downlink resources.

This simulator is very modular and the internal logic of each component can be changed according to specific needs.

According to the idea of Multi-RAT, in this simulator the User Equipment (UE) is not aware of the type of Access Point (AP) it is connecting to. This implies that the UE makes a request in terms of bitrate to one (or more) AP(s).
Each AP, will then compute the actual network resources to be allocated (Resource Blocks for LTE and NR networks, Symbols for Satellite networks) considering the path loss between AP and UE and the inter-AP interference.

This simulator can consider also the movement of UEs, as well as the movement of the APs (with the Drone BaseStation/Relay):
-   UEs have fixed speed and there are two possible movements implemented at this time: 
    -   random movement
    -   line movement given a direction, with bumping on the borders of the map
- Drones move with a  maximum speed towards a certain point; the speed control is done using the unicycle model (without considering orientation)

## Basic steps

The connection process is as follows:

1. UE measures the receiving power for each visible AP
2. According to the measured receiving power (as well as any other variable of interest the programmer can add), it chooses the AP(s) to connect to (in a User-Centric, RAN-Assisted or RAN-Controlled way, depending on the specific needs)
3. The UE sends a connection request to the selected AP(s), indicating its requested bitrate for that connection
4. The AP allocates the resources for the UE’s request based on the SINR in a best-effort manner, notifying the UE the actual bitrate derived from the allocated resources.

In case of moving UEs or APs or in any other specific case, it is possible to update an established connection in order to consider the new path loss, the new SINR or any other change in the connection parameters.
The logic behind the connection update can be personalized according to the specific needs (e.g. reallocation policies and resource contention)

## Resource allocation

As said before the first thing the UE has to do is to measure the receiving power (i.e., the RSRP) of each visible base station. This value depends on four main parameters: the AP antenna power, on the feeder loss, on the antenna gain and on the path loss between the AP and the UE

The path loss model used is the [COST HATA model](https://en.wikipedia.org/wiki/COST_Hata_model) is implemented inside `util.py`, but any other model can be implemented. 

Once a connection request/update is made by an UE, the AP computes the SINR (Signal-to-interference-plus-noise-ratio) in order to determine the bitrate each of its resource blocks can actually provide (using the [Shannon Formula](https://en.wikipedia.org/wiki/Shannon%E2%80%93Hartley_theorem)). Using this value it can compute the number of resource blocks to be allocated for the UE connection.

The interference is computed according to the other APs visible by the UE, to their RSRP, to their utilization ratio and to the utilization ratio of the AP involved in the connection ([reference1](https://ieeexplore.ieee.org/document/6097237), [reference2](https://ieeexplore.ieee.org/document/8826267))

## Usage guidelines

An example of the usage of this simulator can be found in `test.py`. 

The first thing to do is to set-up the environment, indicating the width of the map and the system sampling time

```python
env = environment.wireless_environment(x [, y], sampling_time])
```

Now that the environment is created, it is possible to add UEs using the function

```python
id = insert_ue(ue_class, starting_position = None, speed = 0, direction = 0)
```

where ue_class specifies the bitrate required by the user (see `ue_class` dictionary in `UserEquipment.py`). The starting poisition, if not specified, will be randomly sampled. The speed is in m/s and the direction is in degrees from the positive x axis of the cartesian plan.

At the same way it is possible to add all the APs using the appropriate functions

```python
bs_id = place_SAT_base_station(total_bitrate, position)

bs_id = place_LTE_base_station(position, carrier_frequency, antenna_power, antenna_gain, feeder_loss, available_bandwidth, total_bitrate)

bs_id = place_NR_base_station(position, carrier_frequency, numerology, antenna_power, antenna_gain, feeder_loss, available_bandwidth, total_bitrate)

bs_id = place_DRONE_relay(starting_position, linked_bs_id, carrier_frequency, amplification_factor, antenna_gain, feeder_loss)

bs_id = place_DRONE_base_station(position, carrier_frequency, numerology, antenna_power, antenna_gain, feeder_loss, available_bandwidth, total_bitrate)
```

If specific actions has to be done before the first simulation step, they can be added in the `initial_timestep()` function of `environment.py` or `UserEquipment.py` or in the appropriate AP class.
This function should be explicitly called before starting the simulation (i.e., after all the UEs and APs are placed).

```python
env.initial_timestep()
```

At the same way, if specific actions has to be done after each simulation step, they can be added in the `next_timestep()` function of `environment.py` or `UserEquipment.py` or in the appropriate AP class.
Same as before, this function has to be explicitely called at the end of each timestep in order to let the system move to the next one.

```python
env.next_timestep()
```

Each of the APs has already implemented some common functions, that can be used for specific needs:

- `compute_rbur()` that returns the mean utilization ratio of the AP
- `compute_sinr(rsrp)` that takes a dictionary with the RSRP values of each of the visible APs (it can be generated using the function `env.discover_bs(ue_id)`, that given an UE id finds all the visible APs together with their RSRP values) and returns the SINR value (as real number, not in dB)
- `request_connection(ue_id, data_rate, rsrp)` that given the UE id, the desired data rate for this connection and the RSRP dictionary, allocates the resources for the connection and returns the actual data rate.
- `request_disconnection(ue_id)` that given the UE id releases the resources for its connection
- `update_connection(ue_id, data_rate, rsrp)`, that given the UE id, the desired data rate and the new RSRP dictionary updates the connection (allocating more/less resource blocks) and returns the new actual data rate
- `get_state()` that returns the number of resource block of the AP and the occupied ones
- `get_connection_info(ue_id)` that given the UE id returns the number of resource blocks occupied by the selected UE and the total number of resource blocks of the AP
- `get_connected_users()` that returns the list of all the UEs connected to the AP
- `reset()` that resets the state variable of the AP (here it is possible to add other actions for specific needs)





