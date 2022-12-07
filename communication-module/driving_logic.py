
class driving_logic:
    def __init__(self, node_list, direction_list):
        self.left_stop_found = False
        self.right_stop_found = False
        self.intersection_found = False
        self.lost_intersection = False
        self.stop = False
        self.node_list, self.direction_list = node_list, direction_list
        self.drive_index = 0
        self.drive_right = False
        self.drive_left = False
        self.drive_forward = False
        self.drive_intersection = False

    def drive(self, debug = False):
        if self.drive_intersection is True:
            self.intersection_driving(self, debug)
        else:
            self.normal_driving(self, debug)

    def normal_driving(self, debug=False):
        if self.drive_index < len(self.node_list): #if we have not reached our end destination
            direction_to_drive = str(self.direction_list[self.drive_index])[0]
            stop_to_look_for = str(self.node_list[self.drive_index])[0]
            if stop_to_look_for == "L": #if we are supposed to be looking for a left stop
                if debug:
                    print(" ----- Looking for a left stop ----- \n")
                if self.left_stop_found is True:
                    if debug:
                     print(f"Found a left stop. Previous driving direction was: {self.direction_list[self.drive_index]} New driving direction is FORWARD \n node before update: {self.node_list[self.drive_index]} \n Drive index before update: {self.drive_index}\n --- \n")

                    self.drive_forwards()
                    self.drive_index += 1
                    self.stop = False
                if debug:
                    print("Found nothing now driving: " + self.direction_list[self.drive_index] + "\n looking for: " + self.node_list[
                        self.drive_index] + f"\n with index: {self.drive_index}"
                         + "\n --- \n")
            elif stop_to_look_for == "R":   #if we are supposed to be looking for a right stop
                if debug:
                    print(" ----- Looking for a right stop ----- \n")
                if self.right_stop_found is True:

                    if debug:
                        print(f"Found a right stop. Previous driving direction was: {self.direction_list[self.drive_index]} New driving direction is FORWARD \n node before update: {self.node_list[self.drive_index]} \n Drive index before update: {self.drive_index}\n --- \n")

                    self.drive_forwards()
                    self.drive_index += 1
                    self.stop = False

                if debug:
                    print("Found nothing now driving: " + self.direction_list[self.drive_index] + "\n looking for: " + self.node_list[
                        self.drive_index] + f"\n with index: {self.drive_index}"
                          + "\n --- \n")
            else:
                if debug:
                    print("  -----  Looking for an intersection  ----- \n")
                if self.intersection_found is True:   #if we are supposed to be looking for an intersection
                    if direction_to_drive == "F":    #If we are supposed to be driving forward in the intersection
                        if debug:
                            print("Found intersection, going to be driving: " + self.direction_list[self.drive_index] + "\n just found: " +
                                  self.node_list[self.drive_index] + f"\n Index before update: {self.drive_index}"
                                  + "\n --- \n")
                        # return drive_forward , drive_left, drive_right , drive_index, drive_intersection, stop
                        self.drive_forwards()
                        self.drive_index += 1
                        self.drive_intersection = True
                        self.stop = False
                    elif direction_to_drive == "L":    #If we are supposed to be driving left in the intersection
                        if debug:
                            print("Found intersection, going to be driving driving: " + self.direction_list[self.drive_index] + "\n just found: " +
                                  self.node_list[self.drive_index] + f"\n Index before update: {self.drive_index}"
                                  + "\n --- \n")
                        self.drive_to_right()
                        self.drive_index += 1
                        self.drive_intersection = True
                        self.stop = False
                        # return drive_forward , drive_left, drive_right , drive_index, drive_intersection, stop
                    elif direction_to_drive == "R":    #If we are supposed to be driving right in the intersection
                        if debug:
                            print("Found intersection, going to be driving: " + self.direction_list[self.drive_index] + "\n just found: " +
                                  self.node_list[self.drive_index] + f"\n Index before update: {self.drive_index}"
                                  + "\n --- \n")
                        self.drive_to_right()
                        self.drive_index += 1
                        self.drive_intersection = True
                        self.stop = False
                        # return drive_forward , drive_left, drive_right , drive_index, drive_intersection, stop
                if debug:
                    print("Found nothing now driving: " + self.direction_list[self.drive_index - 1] + "\n looking for: " + self.node_list[self.drive_index] + f"\n with index: {self.drive_index}"
                          + "\n --- \n")
        else:
            if debug:
                print("Found END stop now driving: " + f"\n End index: {self.drive_index}"
                      + "\n --- \n")
            self.drive_forwards()
            self.stop = True
            # we are at the end of the list, therefore we have reached our destination
    
    def intersection_driving(self, debug= False):
        if self.lost_intersection is True:  # Lost intersection is the sign that we have lost the first intersection line
            if self.intersection_found is True:  # if we have found the second intersection line, break
                if debug:
                    print("Found Exit to intersection while driving: " + self.direction_list[self.drive_index - 1] + "\n Returning to normal driving and looking for: " + self.node_list[
                        self.drive_index] + f"\n with index: {self.drive_index}"
                        + "\n --- \n")
                self.drive_intersection = False
                self.lost_intersection = False
                self.drive_forwards()
            if debug:
                print("Driving in intersection, have lost the first one, currently driving: " + self.direction_list[self.drive_index - 1] + "\n looking for exit to intersection, next node is: " + self.node_list[
                    self.drive_index] + f"\n with index: {self.drive_index}"
                      + "\n --- \n")
        elif self.intersection_found is False:  # if we are in an intersection but have lost the intersection line for the first time
            if debug:
                print("Lost sight of the first intersection line currently driving: " + self.direction_list[self.drive_index - 1] + "\n looking for intersection exit, next node is: " + self.node_list[
                    self.drive_index] + f"\n with index: {self.drive_index}"
                      + "\n --- \n")
            self.lost_intersection = True
        else:
            if debug:
                print("we are still looking at the first intersection line, going to be driving: " + self.direction_list[self.drive_index - 1] + "\n node after intersection: " + self.drive_index[
                    self.drive_index] + f"\n with index: {self.drive_index}"
                      + "\n --- \n")
            pass


    def drive_forwards(self):
        self.drive_forward = True
        self.drive_left = False
        self.drive_right = False

    def drive_to_right(self):
        self.drive_forward = False
        self.drive_left = False
        self.drive_right = True

    def drive_to_left(self):
        self.drive_forward = False
        self.drive_left = True
        self.drive_right = False

    
if __name__ == "__main__":
    logic_unit = driving_logic(['LA', 'Kors 1', 'RE', 'LF', 'Kors 2' ,'RB'], ['FORWARD', 'RIGHT', 'FORWARD', 'FORWARD', 'RIGHT', 'STOP'])
