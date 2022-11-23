all_paths = []

class Node:
    def __init__(self,name,x,y):
        self.name = name
        self.x = x
        self.y = y
        self.neighbours = []
        self.explored = False
        self.prev = None

    def add_Edge(self,destinationnode):
        self.neighbours.append(destinationnode)

    def right_direction(self,prevnode,nextnode):
        if prevnode == None:
            return True
        return not((prevnode.x == nextnode.x) and (prevnode.y == nextnode.y))
    
    def __repr__(self):
        return self.name

    def get_direction(self,prevnode,destination):

        if destination == None:
            return "STOP"
        
        if (self.name != "Kors 1" and self.name != "Kors 2") or prevnode.x == destination.x:
            return "FORWARD"
        

        dirx = self.x - prevnode.x
        diry = self.y - prevnode.y
        #print("dirx,diry {0},{1}".format(dirx,diry))

        currentx = self.x
        currenty = self.y
        destx = destination.x
        desty =destination.y
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
        
        dir2x = currentx - destx
        dir2y = currenty - desty

        #print("dirx2,diry2 {0},{1}".format(dir2x,dir2y))
        

        if dir2x == 1 and dir2y == 0:
            return "LEFT"
        elif dir2x == -1 and dir2y == 0:
            return "RIGHT"
        else:##Kommer aldrig hamna här
            return "SAAAY WHATT??"
        #Continue with this



class Graph:
    def __init__(self):
        self.nodelist = []
        self.size = 0
        self.pickup_path = []
        self.pickup_directions = []
        self.dropoff_path = []
        self.dropoff_directions = []

    def add_node(self,node):
        self.nodelist.append(node)
        self.size += 1

    def reset_exploration(self):
        for i in range(self.size-1):
            self.nodelist[i].explored = False
            self.nodelist[i].prev = None

    def find_node(self,node):
        for i in range(self.size-1):
            if self.nodelist[i].name == node:
                return self.nodelist[i]
    

        

    
    def BFS(self,start_node,dest_node):
        self.reset_exploration()
        queue = []
        print("1")
        startnode = self.find_node(start_node)
        startnode.explored = True
        queue.append(startnode)
        endnode = self.find_node(dest_node)
        current = None
        print("2")

        while len(queue) != 0:
            current = queue.pop(0)
            #for i in current.neighbours:
            i = 0
            print("3")

            while i < len(current.neighbours): 
                if(current.neighbours[i].explored == False):
                    queue.append(current.neighbours[i])
                    current.neighbours[i].prev = current
                    current.neighbours[i].explored = True
                i+=1
            if (current.name == endnode.name):
                break
            current.explored = True
        print("Hej")
        path = []
        while current != None:
            path.append(current)
            current = current.prev
            print("Tjabba ")
        return path

    def print_a_path(self,path):
        sizeof_pickup_path = len(path)
        i = 0
        stringtoprint = ""
        while i < sizeof_pickup_path:
            stringtoprint += path[i].name
            if i < sizeof_pickup_path-1:
                stringtoprint += " -->"
            i+=1
        print(stringtoprint)

    def DFS(self,prevnode,current,destination,templist):
        global all_paths 
        templist.append(current)
        current.explored = True
        if (current.name == destination.name):
            all_paths.append(templist)
            current.explored = False
            return True
        i = 0
        while i < len(current.neighbours):
            if((current.neighbours[i].explored == False) and (current.right_direction(prevnode,current.neighbours[i]))):
                if(self.DFS(current,current.neighbours[i],destination,templist.copy()) == False):
                    current.explored = False 
            i+=1
        current.explored = False
        return False

    def DFS_start(self,start_node,dest_node):
        global all_paths
        all_paths = []
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
        #print(all_paths)
        while i < len(all_paths):
            if(length > len(all_paths[i])):
                length = len(all_paths[i])
                indexoflength = i
                path = all_paths[i]
            elif length == len(all_paths[i]):
                testpath = all_paths[indexoflength]
                for nodes in testpath:
                    if ("RF" == nodes.name) or ("LF" == nodes.name) or ("RE" == nodes.name) or ("LE" == nodes.name):
                        path = testpath
                for nodes in all_paths[i]:
                    if ("RF" == nodes.name) or ("LF" == nodes.name) or ("RE" == nodes.name) or ("LE" == nodes.name):
                        path = all_paths[i]

            i+=1
        return path


    def print_path(self,container):
        containersize = len(container)
        i = 0
        stringtoprint = ""
        while i < containersize:
            stringtoprint += container[i].name
            if i < containersize-1:
                stringtoprint += " --> "
            i+=1
        print(stringtoprint+"\n")

    def print_directions(self,container):
        containersize = len(container)
        i = 0
        stringtoprint = ""
        while i < containersize:
            stringtoprint += container[i]
            if i < containersize-1:
                stringtoprint += " --> "
            i+=1
        print(stringtoprint+"\n")

    def print_paths_and_directions(self):
        self.print_path(self.pickup_path)
        self.print_directions(self.pickup_directions)
        self.print_path(self.dropoff_path)
        self.print_directions(self.dropoff_directions)

        
    
    def get_paths_BFS(self,start_node1,start_node2,endnode2):
        self.pickup_path = self.BFS(start_node1,start_node2)
        self.dropoff_path = self.BFS(start_node2,endnode2)
    
    def get_paths_DFS(self,start_node1,start_node2,endnode2):
        self.pickup_path = self.DFS_start(start_node1,start_node2)
        self.dropoff_path = self.DFS_start(start_node2,endnode2)

    def get_directions(self):
        prevnode = None
        last = None
        self.pickup_path.append(last)
        i=0
        while i < len(self.pickup_path):
            if self.pickup_path[i] != None:
                #print(self.pickup_path[i].get_direction(prevnode,self.pickup_path[i+1]))
                self.pickup_directions.append(self.pickup_path[i].get_direction(prevnode,self.pickup_path[i+1]))
                prevnode = self.pickup_path[i]
            i+=1

        self.pickup_path.pop()
        #print("\n\n")
        prevnode = None
        last = None
        self.dropoff_path.append(last)
        i=0
        while i < len(self.dropoff_path):
            if self.dropoff_path[i] != None:
                #print(self.dropoff_path[i].get_direction(prevnode,self.dropoff_path[i+1]))
                self.dropoff_directions.append(self.dropoff_path[i].get_direction(prevnode,self.dropoff_path[i+1]))
                prevnode = self.dropoff_path[i]
            i+=1
        self.dropoff_path.pop()
        #print("\n\n")





        

def main():
    Graph_1 = Graph()

    #Creating all nodes
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

    #Linking all nodes

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
    
    Graph_1.get_paths_DFS("RF","LB","RA")


    Graph_1.get_directions()
    Graph_1.print_paths_and_directions()


main()
