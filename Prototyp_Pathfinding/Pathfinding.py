
class Node:
    #All apropriate members sucha as name, coordinates adjacencylist and a explored variable for the pathfinding algorithm
    def __init__(self,name,x,y):
        self.name = name
        self.x = x
        self.y = y
        self.neighbours = []
        self.explored = False

    #We add a node to the current nodes adjacencylist
    def add_Edge(self,destinationnode):
        self.neighbours.append(destinationnode)

    #We check if the nextnode is not located on the same location as the previous node 
    def right_direction(self,prevnode,nextnode):
        if prevnode == None:
            return True
        return not((prevnode.x == nextnode.x) and (prevnode.y == nextnode.y))
    
    #This function will be called when we want to print a list of nodes 
    def __repr__(self):
        return self.name

    #This function will be called when we want to convert the node to a string 
    def __str__(self):
        return self.name

    #This function calculates where the destination node is located relative to the taxicars current traveldirection
    def get_direction(self,prevnode,destination):

        #If the destination == None then current is the last node which means that we should stop
        if destination == None:
            return "STOP"
        
        #We only have to calculate the turns when we are in intersections since otherwise we just follow the road
        if (self.name != "Kors 1" and self.name != "Kors 2") or prevnode.x == destination.x:
            return "FORWARD"
        

        #calculating the direction from the previous node to where we currently are
        dirx = self.x - prevnode.x
        diry = self.y - prevnode.y


        currentx = self.x
        currenty = self.y
        destx = destination.x
        desty = destination.y
        
        #Inorder to get the correct relative direction we have to make the logic consistent nomather what previous direction we had
        #Inorder to get consistent logic we have to rotate the coordinates depending on what direction we had prevously
        if dirx == 1 : ## If we go to the right
            ##counterclockwise rotation x,y -> -y,x
            currentx = -self.y
            currenty = self.x
            destx = -destination.y
            desty = destination.x

        elif dirx == -1: ## If we go to the left
            ##clockwise rotation x,y -> y,-x
            currentx = self.y
            currenty = -self.x
            destx = destination.y
            desty = -destination.x

        elif diry == -1: ## If we go down
            ## 180 rotation x,y -> -x,-y
            currentx = -self.x
            currenty = -self.y
            destx = -destx
            desty = -desty
        
        #Calculate the new relative direction after we rotated the coordinates
        dir2x = destx - currentx
        dir2y = desty - currenty
        
        # direction (-1,0) is to the left
        if dir2x == -1 and dir2y == 0:
            return "LEFT"
        # dirction (1,0) is to the right
        elif dir2x == 1 and dir2y == 0:
            return "RIGHT" 
        else:##Will never get to here since all the other cases have been covered by above logic
            return "SAAAY WHATT??"
        #Continue with this


class Graph:
    #The constructor for the graph, initializing all variables such as nodelist,    
    def __init__(self):
        self.nodelist = []
        #All nodes we we will visit inorder to get to the pickup location will be in this list
        self.pickup_path = []
        #The directions we will take will be in this list
        self.pickup_directions = []
        #All nodes we we will visit inorder to get to the dropoff location will be in this list
        self.dropoff_path = []
        #The directions we will take will be in this list
        self.dropoff_directions = []
        #We will save all the paths in this list before we pick the shortest path, it is a somewhat of a bruteforce approach
        self.all_paths = []

    #Adding nodes to the graph
    def add_node(self,node):
        self.nodelist.append(node)

    #before we start exploring the graph we want to reset exploration
    def reset_exploration(self):
        for i in range(len(self.nodelist)):
            self.nodelist[i].explored = False

    #finding a particular node with the name nodename
    def find_node(self,nodename):
        for i in range(len(self.nodelist)):
            if self.nodelist[i].name == nodename:
                return self.nodelist[i]

    #This is the pathfining algorithm a DFS, DFS does NOT normaly give the shortest path, which is true but in this case we get ALL paths that reach the destination
    #So that we can get the shortest path
    def DFS(self,prevnode,current,destination,templist):
        templist.append(current)
        current.explored = True
        if (current.name == destination.name):
            self.all_paths.append(templist)
            current.explored = False
            return True
        i = 0
        while i < len(current.neighbours):
            #Check if the node adjacent node have been visited and make sure that is located in the right direction, 
            #in this case it mean that it cannot be located behind the current node relative to the current diection
            if((current.neighbours[i].explored == False) and (current.right_direction(prevnode,current.neighbours[i]))):
                #I want an explicit copy since i dont want to use a reference in this case which is why i provide
                # a copy of templist to the next depth of the recursive call
                if(self.DFS(current,current.neighbours[i],destination,templist.copy()) == False):
                    #current.explored = False
                    pass
            i+=1
        current.explored = False
        return False

    #Initializing the DFS algorithm and get the shortest path from it
    def DFS_start(self,start_node,dest_node):
        self.all_paths = []
        self.reset_exploration()
        startnode = self.find_node(start_node)
        startnode.explored = True
        endnode = self.find_node(dest_node)
        previous = None
        startlist = []
        self.DFS(previous,startnode,endnode,startlist)
        path = []
        length = 100000
        indexoflength = -1
        i=0
        while i < len(self.all_paths):
        #Chosing the path with the least amount of nodes in it
            if(length > len(self.all_paths[i])):
                length = len(self.all_paths[i])
                indexoflength = i
                path = self.all_paths[i]
        #if there are two paths with the same amount of nodes in it we chose the path that goes through the middle of the map ie where "RF","LF","RE", "LE" are located 
            elif length == len(self.all_paths[i]):
                testpath = self.all_paths[indexoflength]
                for nodes in testpath:
                    if ("RF" == nodes.name) or ("LF" == nodes.name) or ("RE" == nodes.name) or ("LE" == nodes.name):
                        path = testpath
                for nodes in self.all_paths[i]:
                    if ("RF" == nodes.name) or ("LF" == nodes.name) or ("RE" == nodes.name) or ("LE" == nodes.name):
                        path = self.all_paths[i]
            i+=1
        return path

    #This simply prints the path of a container with the path
    def print_container(self,container):
        containersize = len(container)
        i = 0
        stringtoprint = ""
        while i < containersize:
            #Converting what is in the container to a string so it can be combined with stringtoprint, this is done by the __str__ operator 
            stringtoprint += str(container[i])
            if i < containersize-1:
                stringtoprint += " --> "
            i+=1
        print(stringtoprint+"\n")

    #Printing all paths and all turndirections
    def print_paths_and_directions(self):
        self.print_container(self.pickup_path)
        self.print_container(self.pickup_directions)
        self.print_container(self.dropoff_path)
        self.print_container(self.dropoff_directions)

    #Calling DFS_start so that we get tha shortest path for pickup path and dropoff path
    def get_paths_DFS(self,start_node1,start_node2,endnode2):
        self.pickup_path = self.DFS_start(start_node1,start_node2)
        self.dropoff_path = self.DFS_start(start_node2,endnode2)

    #Getting all the turndirecitons for the 
    def get_directions(self):
        prevnode = None
        #last = None which determines the stopcondition --> it will make the last element of the turndirections be "STOP"
        last = None
        self.pickup_path.append(last)
        i=0
        while i < len(self.pickup_path):
            if self.pickup_path[i] != None:
                self.pickup_directions.append(self.pickup_path[i].get_direction(prevnode,self.pickup_path[i+1]))
                prevnode = self.pickup_path[i]
            i+=1

        self.pickup_path.pop()
        prevnode = None
        last = None
        self.dropoff_path.append(last)
        i=0
        while i < len(self.dropoff_path):
            if self.dropoff_path[i] != None:
                self.dropoff_directions.append(self.dropoff_path[i].get_direction(prevnode,self.dropoff_path[i+1]))
                prevnode = self.dropoff_path[i]
            i+=1
        self.dropoff_path.pop()




        

def main():
    Graph_1 = Graph()

    #Creating all nodes which is a representation of our current map
    RA = Node("RA",0,0)
    LA = Node("LA",0,0)
    
    RB = Node("RB",3,0)
    LB = Node("LB",3,0)
    
    RC = Node("RC",3,2)
    LC = Node("LC",3,2)
    
    RD = Node("RD",0,2)
    LD = Node("LD",0,2)
    
    Korsning_1 = Node("Kors 1",0,1)
    Fake_Korsning_1 = Node("Kors 1",0,1)
    
    RE = Node("RE",1,1)
    LE = Node("LE",1,1)
    
    RF = Node("RF",2,1)
    LF = Node("LF",2,1)   

    Korsning_2 = Node("Kors 2",3,1)
    Fake_Korsning_2 = Node("Kors 2",3,1)

    Graph_1.add_node(RA)
    Graph_1.add_node(LA)
    Graph_1.add_node(RB)
    Graph_1.add_node(LB)
    Graph_1.add_node(RC)
    Graph_1.add_node(LC)
    Graph_1.add_node(RD)
    Graph_1.add_node(LD)
    Graph_1.add_node(RE)
    Graph_1.add_node(LE)
    Graph_1.add_node(RF)
    Graph_1.add_node(LF)
    Graph_1.add_node(Korsning_1)
    Graph_1.add_node(Fake_Korsning_1)
    Graph_1.add_node(Korsning_2)
    Graph_1.add_node(Fake_Korsning_2)

    #Linking all nodes correctly

    RA.add_Edge(LB)
    LA.add_Edge(Korsning_1)

    RB.add_Edge(LA)
    LB.add_Edge(Korsning_2)

    RC.add_Edge(Korsning_2)
    LC.add_Edge(RD)

    RD.add_Edge(Korsning_1)
    LD.add_Edge(RC)

    RE.add_Edge(LF)
    LE.add_Edge(Fake_Korsning_1)

    RF.add_Edge(LE)
    LF.add_Edge(Fake_Korsning_2)

    Korsning_1.add_Edge(LD)
    Korsning_1.add_Edge(RA)
    Korsning_1.add_Edge(RE)

    Fake_Korsning_1.add_Edge(LD)
    Fake_Korsning_1.add_Edge(RA)

    Korsning_2.add_Edge(RB)
    Korsning_2.add_Edge(LC)
    Korsning_2.add_Edge(RF)

    Fake_Korsning_2.add_Edge(LC)
    Fake_Korsning_2.add_Edge(RB)
    
    Graph_1.get_paths_DFS("LA","LB","RD")


    Graph_1.get_directions()
    Graph_1.print_paths_and_directions()


main()
