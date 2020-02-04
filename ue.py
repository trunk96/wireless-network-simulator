class user_equipment:
    requested_bitrate = 0
    ue_id = None
    current_position = None
    h_m = 1 #height of UE antenna

    def __init__ (self, requested_bitrate, ue_id, starting_position):
        self.ue_id = ue_id
        self.requested_bitrate = requested_bitrate
        self.current_position = (starting_position[0], starting_position[1])
        self.h_m = starting_position[2]

    def move(self):
        return
    

    
