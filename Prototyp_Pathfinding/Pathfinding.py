


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

all_paths = []

class Graph:
    def __init__(self):
        self.nodelist = []
        self.size = 0
        self.pickup_path = []
        self.dropoff_path = []

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

    def DFS(self,prevnode,current,destination,templist):
        global all_paths
        global recursiondepth
        print("Recursiondepth = ",recursiondepth)
        recursiondepth +=1
        
        templist.append(current)
        current.explored = True
        if (current.name == destination.name):
            print("Hej")
            all_paths.append(templist)
            current.explored = False
            recursiondepth -= 1
            return True
        i = 0
        while i < len(current.neighbours):
            if((current.neighbours[i].explored == False) and (current.right_direction(prevnode,current.neighbours[i]))):
                if(self.DFS(current,current.neighbours[i],destination,templist.copy()) == False):
                    current.explored = False 
            i+=1
        recursiondepth -=1

        return False

    def DFS_start(self,start_node,dest_node):
        global all_paths
        all_paths = []
        global recursiondepth
        recursiondepth = 0
        self.reset_exploration()
        startnode = self.find_node(start_node)
        startnode.explored = True
        endnode = self.find_node(dest_node)
        previous = None
        startlist = []
        self.DFS(previous,startnode,endnode,startlist)

        path = []
        length = 100000
        i=0
        while i < len(all_paths):
            if(length > len(all_paths[i])):
                length = len(all_paths[i])
                path = all_paths[i]
            i+=1
        return path

    def print_paths(self):
        sizeof_pickup_path = len(self.pickup_path)
        i = 0
        stringtoprint = ""
        while i < sizeof_pickup_path:
            stringtoprint += self.pickup_path[i].name
            if i < sizeof_pickup_path-1:
                stringtoprint += " -->"
            i+=1
        print(stringtoprint+"\n")
        stringtoprint = ""
        sizeof_dropoffpath = len(self.dropoff_path)
        i = 0
        while i < sizeof_dropoffpath:
            stringtoprint += self.dropoff_path[i].name
            if i < sizeof_dropoffpath-1:
                stringtoprint += " -->"
            i+=1
        print(stringtoprint+"\n")
            
        
    
    def get_paths_BFS(self,start_node1,start_node2,endnode2):
        self.pickup_path = self.BFS(start_node1,start_node2)
        self.dropoff_path = self.BFS(start_node2,endnode2)
    
    def get_paths_DFS(self,start_node1,start_node2,endnode2):
        self.pickup_path = self.DFS_start(start_node1,start_node2)
        self.dropoff_path = self.DFS_start(start_node2,endnode2)





        

def main():
    Graph_1 = Graph()

    #Creating all nodes
    A = Node("A",0,0)
    Fake_A = Node("Fake A",0,0)
    B = Node("B",1,0)
    Fake_B = Node("Fake B",2,0)
    C = Node("C",1,2)
    Fake_C = Node("Fake C",2,2)
    D = Node("D",0,2)
    Fake_D = Node("Fake D",0,2)
    Korsning_1 = Node("Kors 1",0,1)
    Fake_Korsning_1 = Node("Fake Kors 1",0,1)
    E = Node("E",1,1)
    F = Node("F",1,1)
    Korsning_2 = Node("Kors 2",2,1)
    Fake_Korsning_2 = Node("Fake Kors 2",2,1)

    Graph_1.add_node(A)
    Graph_1.add_node(Fake_A)
    Graph_1.add_node(B)
    Graph_1.add_node(Fake_B)
    Graph_1.add_node(C)
    Graph_1.add_node(Fake_C)
    Graph_1.add_node(D)
    Graph_1.add_node(Fake_D)
    Graph_1.add_node(E)
    Graph_1.add_node(F)
    Graph_1.add_node(Korsning_1)
    Graph_1.add_node(Fake_Korsning_1)
    Graph_1.add_node(Korsning_2)
    Graph_1.add_node(Fake_Korsning_2)

    #Linking all nodes

    A.add_Edge(Korsning_1)
    Fake_A.add_Edge(B)

    B.add_Edge(Korsning_2)
    Fake_B.add_Edge(A)
    
    Korsning_1.add_Edge(D)
    Korsning_1.add_Edge(Fake_A)
    Korsning_1.add_Edge(E)

    Fake_Korsning_1.add_Edge(Fake_A)
    Fake_Korsning_1.add_Edge(D)

    Korsning_2.add_Edge(Fake_B)
    Korsning_2.add_Edge(C)
    Korsning_2.add_Edge(F)
    
    Fake_Korsning_2.add_Edge(C)
    Fake_Korsning_2.add_Edge(Fake_B)

    Fake_C.add_Edge(Korsning_2)
    C.add_Edge(Fake_D)

    D.add_Edge(Fake_C)
    Fake_D.add_Edge(Korsning_1)

    F.add_Edge(Fake_Korsning_1)

    E.add_Edge(Fake_Korsning_2)
    
    Graph_1.get_paths_DFS("A","C","D")
    Graph_1.print_paths()

main()
