class driving_logic:
    def __init__(self, node_list, direction_list):
        self.left = False
        self.right = False
        self.intersection = False
        self.lost_intersection = False
        self.stop = False
        self.node_list, self.direction_list = node_list, direction_list
        self.drive_index = 0
        self.drive_right = False
        self.drive_left = False
        self.drive_forward = True # False
        self.drive_intersection = False

    def look_for_left_lane(self) -> bool:
        return self.drive_left or self.drive_forward

    def look_for_right_lane(self) -> bool:
        return self.drive_right or self.drive_forward

    def normal_driving(self):
        if self.drive_index < len(self.node_list): #if we have not reached our end destination
            if str(self.node_list[self.drive_index])[0] == "L": #if we are supposed to be looking for a left stop
                print(" ----- Looking for a left stop ----- \n")
                if self.left is True:
                    print(f"Found a left stop. Previous driving direction was: {self.direction_list[self.drive_index]} New driving direction is FORWARD \n node before update: {self.node_list[self.drive_index]} \n Drive index before update: {self.drive_index}\n --- \n")
                    # return drive_forward , drive_left, drive_right , drive_index, drive_intersection, stop
                    self.drive_forward = True
                    self.drive_left = False
                    self.drive_right = False
                    self.drive_index += 1
                    self.drive_intersection = False
                    self.stop = False
                print("Found nothing now driving: " + self.direction_list[self.drive_index] + "\n looking for: " + self.node_list[
                    self.drive_index] + f"\n with index: {self.drive_index}"
                      + "\n --- \n")
            elif str(self.node_list[self.drive_index])[0] == "R":   #if we are supposed to be looking for a right stop
                print(" ----- Looking for a right stop ----- \n")
                if self.right is True:
                    print(f"Found a right stop. Previous driving direction was: {self.direction_list[self.drive_index]} New driving direction is FORWARD \n node before update: {self.node_list[self.drive_index]} \n Drive index before update: {self.drive_index}\n --- \n")
                    self.drive_forward = True
                    self.drive_left = False
                    self.drive_right = False
                    self.drive_index += 1
                    self.drive_intersection = False
                    self.stop = False
                print("Found nothing now driving: " + self.direction_list[self.drive_index] + "\n looking for: " + self.node_list[
                    self.drive_index] + f"\n with index: {self.drive_index}"
                      + "\n --- \n")
            else:
                print("  -----  Looking for an intersection  ----- \n")
                if self.intersection is True:   #if we are supposed to be looking for an intersection
                    if str(self.direction_list[self.drive_index])[0] == "F":    #If we are supposed to be driving forward in the intersection
                        print("Found intersection, going to be driving: " + self.direction_list[self.drive_index] + "\n just found: " +
                              self.node_list[self.drive_index] + f"\n Index before update: {self.drive_index}"
                              + "\n --- \n")
                        # return drive_forward , drive_left, drive_right , drive_index, drive_intersection, stop
                        self.drive_forward = True
                        self.drive_left = False
                        self.drive_right = False
                        self.drive_index += 1
                        self.drive_intersection = True
                        self.stop = False
                    elif str(self.direction_list[self.drive_index])[0] == "L":    #If we are supposed to be driving left in the intersection
                        print("Found intersection, going to be driving driving: " + self.direction_list[self.drive_index] + "\n just found: " +
                              self.node_list[self.drive_index] + f"\n Index before update: {self.drive_index}"
                              + "\n --- \n")
                        self.drive_forward = False
                        self.drive_left = True
                        self.drive_right = False
                        self.drive_index += 1
                        self.drive_intersection = True
                        self.stop = False
                        # return drive_forward , drive_left, drive_right , drive_index, drive_intersection, stop
                    elif str(self.direction_list[self.drive_index])[0] == "R":    #If we are supposed to be driving right in the intersection
                        print("Found intersection, going to be driving: " + self.direction_list[self.drive_index] + "\n just found: " +
                              self.node_list[self.drive_index] + f"\n Index before update: {self.drive_index}"
                              + "\n --- \n")
                        self.drive_forward = False
                        self.drive_left = False
                        self.drive_right = True
                        self.drive_index += 1
                        self.drive_intersection = True
                        self.stop = False
                        # return drive_forward , drive_left, drive_right , drive_index, drive_intersection, stop
                print("Found nothing now driving: " + self.direction_list[self.drive_index - 1] + "\n looking for: " + self.node_list[self.drive_index] + f"\n with index: {self.drive_index}"
                      + "\n --- \n")
        else:
            print("Found END stop now driving: " + f"\n End index: {self.drive_index}"
                  + "\n --- \n")
            self.drive_forward = False
            self.drive_left = False
            self.drive_right = False
            self.drive_intersection = False
            self.stop = True
            # we are at the end of the list, therefore we have reached our destination
    
    def intersection_driving(self):
        if self.lost_intersection is True:  # Lost intersection is the sign that we have lost the first intersection line
            if self.intersection is True:  # if we have found the second intersection line, break
                print(
                    "Found Exit to intersection while driving: " + self.direction_list[self.drive_index - 1] + "\n Returning to normal driving and looking for: " + self.node_list[
                        self.drive_index] + f"\n with index: {self.drive_index}"
                    + "\n --- \n")
                self.drive_intersection = False
                self.lost_intersection = False
                self.drive_forward = True
                self.drive_right = False
                self.drive_left = False
                # ret drive_intersection, lost_intersection, drive_forward, drive_right, drive_left
            print("Driving in intersection, have lost the first one, currently driving: " + self.direction_list[self.drive_index - 1] + "\n looking for exit to intersection, next node is: " + self.node_list[
                self.drive_index] + f"\n with index: {self.drive_index}"
                  + "\n --- \n")
        elif self.intersection is False:  # if we are in an intersection but have lost the intersection line for the first time
            print("Lost sight of the first intersection line currently driving: " + self.direction_list[self.drive_index - 1] + "\n looking for intersection exit, next node is: " + self.node_list[
                self.drive_index] + f"\n with index: {self.drive_index}"
                  + "\n --- \n")
            self.drive_intersection = True
            self.lost_intersection = True
            # ret drive_intersection, lost_intersection, drive_forward, drive_right, drive_left
        print("we are still looking at the first intersection line, going to be driving: " + self.direction_list[self.drive_index - 1] + "\n node after intersection: " + self.drive_index[
            self.drive_index] + f"\n with index: {self.drive_index}"
              + "\n --- \n")
        self.drive_intersection = False
        self.lost_intersection = False
        # ret drive_intersection, lost_intersection, drive_forward, drive_right, drive_left

