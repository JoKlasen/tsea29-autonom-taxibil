import Pathfinding as path
import detection



def normal_driving(drive_index, node_list, direction_list, left, right, intersection):
    if drive_index < len(node_list): #if we have not reached our end destination
        if str(node_list[drive_index])[0] == "L": #if we are supposed to be looking for a left stop
            if left is True:
                print("Found left stop now driving: " + direction_list[drive_index] + "/n looking for: " + drive_index[drive_index] + "/n with index: " + drive_index
                      + "/n --- /n")
                return True, False, False, drive_index + 1, False, False  # return drive_forward , drive_left, drive_right , drive_index, drive_intersection, stop
            print("Found nothing now driving: " + direction_list[drive_index] + "/n looking for: " + drive_index[
                drive_index] + "/n with index: " + drive_index
                  + "/n --- /n")
        elif str(node_list[drive_index])[0] == "R":   #if we are supposed to be looking for a right stop
            if right is True:
                print("Found right stop now driving: " + direction_list[drive_index] + "/n looking for: " + drive_index[drive_index] + "/n with index: " + drive_index
                      + "/n --- /n")
                return True, False, False, drive_index + 1, False, False  # return drive_forward , drive_left, drive_right , drive_index, drive_intersection, stop
            print("Found nothing now driving: " + direction_list[drive_index] + "/n looking for: " + drive_index[
                drive_index] + "/n with index: " + drive_index
                  + "/n --- /n")
        else:
            if intersection is True:   #if we are supposed to be looking for an intersection
                if str(direction_list[drive_index])[0] == "F":    #If we are supposed to be driving forward in the intersection
                    print("Found intersection now driving: " + direction_list[drive_index] + "/n looking for: " +
                          drive_index[drive_index] + "/n with index: " + drive_index
                          + "/n --- /n")
                    return True, False, False, drive_index + 1, True, False   # return drive_forward , drive_left, drive_right , drive_index, drive_intersection, stop
                elif str(direction_list[drive_index])[0] == "L":    #If we are supposed to be driving left in the intersection
                    print("Found intersection now driving: " + direction_list[drive_index] + "/n looking for: " +
                          drive_index[drive_index] + "/n with index: " + drive_index
                          + "/n --- /n")
                    return False, True, False, drive_index + 1, True, False  # return drive_forward , drive_left, drive_right , drive_index, drive_intersection, stop
                elif str(direction_list[drive_index])[0] == "R":    #If we are supposed to be driving right in the intersection
                    print("Found intersection now driving: " + direction_list[drive_index] + "/n looking for: " +
                          drive_index[drive_index] + "/n with index: " + drive_index
                          + "/n --- /n")
                    return False, False, True, drive_index + 1, True, False  # return drive_forward , drive_left, drive_right , drive_index, drive_intersection, stop
            print("Found nothing now driving: " + direction_list[drive_index] + "/n looking for: " + drive_index[
                drive_index] + "/n with index: " + drive_index
                  + "/n --- /n")
    else:
        print("Found END stop now driving: " + direction_list[drive_index] + "/n looking for: " + drive_index[
            drive_index] + "/n with index: " + drive_index
              + "/n --- /n")
        return False, False, False, drive_index, False, True  # we are at the end of the list, therefore we have reached our destination

def intersection_driving(intersection, lost_intersection, drive_forward, drive_right, drive_left):
    if lost_intersection is True:  # Lost intersection is the sign that we have lost the first intersection line
        if intersection is True:  # if we have found the second intersection line, break
            print(
                "Intersection is lost BUT found next one while driving: " + direction_list[drive_index] + "/n looking for: " + drive_index[
                    drive_index] + "/n with index: " + drive_index
                + "/n --- /n")
            return False, False, True, False, False # ret intersection_driving, lost_intersection, drive_forward, drive_right, drive_left
        print("Intersection is lost and next not found while driving: " + direction_list[drive_index] + "/n looking for: " + drive_index[
            drive_index] + "/n with index: " + drive_index
              + "/n --- /n")
    elif intersection is False:  # if we are in an intersection but have lost the intersection line for the first time
        print("we have lost the intersection line for the first time while driving: " + direction_list[drive_index] + "/n looking for: " + drive_index[
            drive_index] + "/n with index: " + drive_index
              + "/n --- /n")
        return True, True, drive_forward, drive_right, drive_left  # ret intersection_driving, lost_intersection, drive_forward, drive_right, drive_left
    print("we are still looking at the first intersection line: " + direction_list[drive_index] + "/n looking for: " + drive_index[
        drive_index] + "/n with index: " + drive_index
          + "/n --- /n")
    return True, False, drive_forward, drive_right, drive_left # ret intersection_driving, lost_intersection, drive_forward, drive_right, drive_left



