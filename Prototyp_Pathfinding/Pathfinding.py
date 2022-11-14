


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
                else:
                    i+=1
            current.explored = True
        print("Hej")
        path = []
        while current.prev != None:
            path.append(current)
            current = current.prev
            print("Tjabba ")
        return path

    def print_paths(self):
        sizeof_pickup_path = len(self.pickup_path)
        for i in range(sizeof_pickup_path-1):
            stringtoprint = self.pickup_path[i].name
            if i != sizeof_pickup_path-1:
                stringtoprint += " -->"
        print(stringtoprint+"\n")
        stringtoprint = ""
        sizeof_dropoffpath = len(self.dropoff_path)
        for i in range(sizeof_dropoffpath-1):
            stringtoprint = self.dropoff_path[i].name
            if i != sizeof_dropoffpath-1:
                stringtoprint += " -->"
        print(stringtoprint+"\n")
            
        
    
    def get_paths(self,start_node1,start_node2,endnode2):
        self.pickup_path = self.BFS(start_node1,start_node2)
        self.dropoff_path = self.BFS(start_node2,endnode2)





        

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

    Graph_1.get_paths("A","C","D")
    Graph_1.print_paths()

main()
