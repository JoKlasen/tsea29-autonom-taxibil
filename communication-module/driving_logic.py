import Pathfinding as path
import detection



def normal_driving(drive_index, node_list, direction_list, left, right, intersection):
    if drive_index < len(node_list): #if we have not reached our end destination
        if str(node_list[drive_index])[0] == "L": #if we are supposed to be looking for a left stop
            print(" ----- Looking for a left stop ----- \n")
            if left is True:
                print(f"Found a left stop. Previous driving direction was: {direction_list[drive_index]} New driving direction is FORWARD \n node before update: {node_list[drive_index]} \n Drive index before update: {drive_index}\n --- \n")
                return True, False, False, drive_index + 1, False, False  # return drive_forward , drive_left, drive_right , drive_index, drive_intersection, stop
            print("Found nothing now driving: " + direction_list[drive_index] + "\n looking for: " + node_list[
                drive_index] + f"\n with index: {drive_index}"
                  + "\n --- \n")
        elif str(node_list[drive_index])[0] == "R":   #if we are supposed to be looking for a right stop
            print(" ----- Looking for a right stop ----- \n")
            if right is True:
                print(f"Found a right stop. Previous driving direction was: {direction_list[drive_index]} New driving direction is FORWARD \n node before update: {node_list[drive_index]} \n Drive index before update: {drive_index}\n --- \n")
                return True, False, False, drive_index + 1, False, False  # return drive_forward , drive_left, drive_right , drive_index, drive_intersection, stop
            print("Found nothing now driving: " + direction_list[drive_index] + "\n looking for: " + node_list[
                drive_index] + f"\n with index: {drive_index}"
                  + "\n --- \n")
        else:
            print("  -----  Looking for an intersection  ----- \n")
            if intersection is True:   #if we are supposed to be looking for an intersection
                if str(direction_list[drive_index])[0] == "F":    #If we are supposed to be driving forward in the intersection
                    print("Found intersection, going to be driving: " + direction_list[drive_index] + "\n just found: " +
                          node_list[drive_index] + f"\n Index before update: {drive_index}"
                          + "\n --- \n")
                    return True, False, False, drive_index + 1, True, False   # return drive_forward , drive_left, drive_right , drive_index, drive_intersection, stop
                elif str(direction_list[drive_index])[0] == "L":    #If we are supposed to be driving left in the intersection
                    print("Found intersection, going to be driving driving: " + direction_list[drive_index] + "\n just found: " +
                          node_list[drive_index] + f"\n Index before update: {drive_index}"
                          + "\n --- \n")
                    return False, True, False, drive_index + 1, True, False  # return drive_forward , drive_left, drive_right , drive_index, drive_intersection, stop
                elif str(direction_list[drive_index])[0] == "R":    #If we are supposed to be driving right in the intersection
                    print("Found intersection, going to be driving: " + direction_list[drive_index] + "\n just found: " +
                          node_list[drive_index] + f"\n Index before update: {drive_index}"
                          + "\n --- \n")
                    return False, False, True, drive_index + 1, True, False  # return drive_forward , drive_left, drive_right , drive_index, drive_intersection, stop
            print("Found nothing now driving: " + direction_list[drive_index - 1] + "\n looking for: " + node_list[drive_index] + f"\n with index: {drive_index}"
                  + "\n --- \n")
    else:
        print("Found END stop now driving: " + f"\n End index: {drive_index}"
              + "\n --- \n")
        return False, False, False, drive_index, False, True  # we are at the end of the list, therefore we have reached our destination

def intersection_driving(intersection, lost_intersection, drive_forward, drive_right, drive_left, direction_list, node_list, drive_index):
    if lost_intersection is True:  # Lost intersection is the sign that we have lost the first intersection line
        if intersection is True:  # if we have found the second intersection line, break
            print(
                "Found Exit to intersection while driving: " + direction_list[drive_index - 1] + "\n Returning to normal driving and looking for: " + node_list[
                    drive_index] + f"\n with index: {drive_index}"
                + "\n --- \n")
            return False, False, True, False, False # ret intersection_driving, lost_intersection, drive_forward, drive_right, drive_left
        print("Driving in intersection, have lost the first one, currently driving: " + direction_list[drive_index - 1] + "\n looking for exit to intersection, next node is: " + node_list[
            drive_index] + f"\n with index: {drive_index}"
              + "\n --- \n")
    elif intersection is False:  # if we are in an intersection but have lost the intersection line for the first time
        print("Lost sight of the first intersection line currently driving: " + direction_list[drive_index - 1] + "\n looking for intersection exit, next node is: " + node_list[
            drive_index] + f"\n with index: {drive_index}"
              + "\n --- \n")
        return True, True, drive_forward, drive_right, drive_left  # ret intersection_driving, lost_intersection, drive_forward, drive_right, drive_left
    print("we are still looking at the first intersection line, going to be driving: " + direction_list[drive_index - 1] + "\n node after intersection: " + drive_index[
        drive_index] + f"\n with index: {drive_index}"
          + "\n --- \n")
    return True, False, drive_forward, drive_right, drive_left # ret intersection_driving, lost_intersection, drive_forward, drive_right, drive_left



