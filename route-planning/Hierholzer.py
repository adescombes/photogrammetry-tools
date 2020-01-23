# original python code found at https://www.geeksforgeeks.org/hierholzers-algorithm-directed-graph/

import numpy as np
import random
import pandas as pd

# each edge is represented by = [vertex_1, vertex_2, (0:one-way, 1:two-way street)]
sion = [
    [1,2,1],[1,3,1],[1,6,1],[2,3,1],[2,4,1],[3,6,1],[3,9,1],[6,9,1],[3,5,1],
   [4,5,1],[6,7,1],[7,9,1],[7,10,1],[10,3,1],[5,10,1],[11,10,0],[11,5,0],
    [4,15,1],[15,17,1],[17,16,0],[16,15,0],[16,14,1],[16,13,1],[14,15,1],
    [4,13,1],[13,5,1],[13,11,1],[14,5,1],[11,14,1],[14,34,1],[11,34,1],
    [37,10,0],[34,37,1],[40,34,1],[7,8,1],[8,40,1],[8,38,1],[38,40,1],
    [8,19,1],[37,38,1],[36,38,1],[36,37,1],[19,37,1],[19,38,1],[19,20,1],
    [20,21,0],[21,19,1],[21,23,1],[23,24,1],[22,24,1],[22,23,1],[20,22,1],
    [24,25,1],[25,27,1],[25,26,1],[26,27,1],[27,28,1],[26,28,1],[22,27,1],
    [22,28,1],[22,30,1],[28,41,1],[20,31,1],[34,36,1],[31,36,1],[32,36,1],
    [32,34,1],[35,14,1],[34,35,1],[32,35,1],[35,18,0],[14,18,1],[18,50,1],
    [16,50,1],[30,31,1],[30,32,1],[32,45,1],[31,45,1],[30,45,1],[28,30,1],
    [45,46,1],[44,45,1],[30,44,1],[46,47,1],[30,41,1],[41,42,1],[41,43,1],
    [43,47,1],[42,43,1],[43,47,1],[45,35,1],[44,46,1],[41,44,1],[43,44,1],
    [50,52,1],[48,52,1],[47,48,1],[47,51,1],[51,52,1],[51,53,1],[53,17,1],
    [51,54,1],[54,55,1],[43,51,1],[53,54,1],[51,16,1],[17,55,1],
    [0,19,1],[0,21,1],[0,23,1]
]

sion_zone_1 = [
    
    [1,2,1],[1,3,1],[1,6,1],[6,9,1],[6,7,1],[3,9,1],[3,6,1],[2,3,1],[2,4,1],[4,5,1],
    [3,5,1],[3,10,1],[7,9,1],[7,10,1],[5,10,1]
]

sion_zone_2 = [
    [4,5,1],[5,10,1],[7,10,1],
    [4,15,1],[4,13,1],[13,15,1],[5,13,1],[11,13,1],[5,11,1],[11,10,0],[37,10,0],[7,8,1],
    [8,19,1],[8,38,1],[8,40,1],[38,40,1],[19,38,1],[37,38,1],[34,40,1],[34,37,1],[11,34,1],
    [11,14,1],[5,14,1],[14,15,1],[13,15,1],[13,16,1],[16,15,0],[34,14,1]
]

sion_zone_3 = [
    [19,20,1],[0,19,1],[19,21,1],[20,21,1],[0,21,1],[0,23,1],[21,23,1],[23,24,1],[22,23,1],[22,24,1],
    [20,22,1],[20,31,1],[24,25,1],[25,26,1],[25,27,1],[26,27,1],[26,28,1],[27,28,1],[22,27,1],[22,28,1],
    [22,30,1],[28,30,1],[30,32,1],[32,36,1],[31,36,1],[31,45,1],[36,38,1],[36,37,1],[34,36,1],[32,34,1],
    [34,37,1],[37,19,1],[37,38,1],[19,38,1], [30,45,1]
]

sion_zone_4 = [
    [32,34,1],[32,35,1],[30,32,1],[14,34,1],[14,16,1],[17,16,0],[16,15,0],[15,17,1],[14,15,1],[17,55,1],[54,55,1],
    [51,54,1],[54,53,1],[51,16,1],[53,17,1],[51,53,1],[51,52,1],[16,50,1],[18,50,1],[35,18,0],[14,18,1],[14,35,1],
    [34,35,1],[35,45,1],[45,46,1],[44,45,1],[30,44,1],[30,41,1],[41,44,1],[43,41,1],[43,44,1],[44,46,1],[43,47,1],
    [46,47,1],[47,48,1],[48,52,1],[50,52,1],[30,28,1],[28,41,1],[42,43,1],[43,51,1]
    
]


def printCircuit(adj): 
  
    # adj represents the adjacency list of 
    # the directed graph 
    # edge_count represents the number of edges 
    # emerging from a vertex 
    # edge_weight represents the number of times the edge
    # is visited (starts at 0, +1 at each visit)
    edge_count = dict() 
    edge_weight = dict()
  
    for i in adj.keys(): 
  
        # find the count of edges to keep track 
        # of unused edges 
        edge_count[i] = len(adj.get(i)) 
        edge_weight[i] = 0
  
    if len(adj) == 0: 
        return # empty graph 
  
    # Maintain a stack to keep vertices 
    curr_path = [] 
  
    # vector to store final circuit 
    circuit = [] 
  
    # start from any vertex 
    curr_v = random.choice([x for x in adj_sion.keys()]) # Current vertex 
    curr_path.append(curr_v) 


    while len(curr_path): 
  
        # If there's remaining edge 
        if edge_count[curr_v]: 
              
            # Push the vertex 
            curr_path.append(curr_v) 
        
            # choices of possible vertices 
            next_v_choices = adj[curr_v]
            
                
            # if the current path is long enough (more than 2 vertices visited), 
            # and the previous-previous vertex is among the choices, 
            # do not consider this option (to avoid 180° turns).
            # There must be more than 1 choice
            if (len(curr_path) > 2) & (len(next_v_choices)>1):
                for v in next_v_choices:
                    if curr_path[-2] == v:
                        next_v_choices.remove(v)
                        #break
            
            # weight of all choices
            next_v_weights = [edge_weight[x] for x in next_v_choices]
        
            min_weight = min(next_v_weights)
            
            # ideally we chose the vertex with the smallest weight, i.e. that has been visited the least
            min_weight_idx = [i for i, x in enumerate(next_v_weights) if x == min_weight]
            # we chose one vertex randomly among those with minimum weight
            
            next_v = random.choice([next_v_choices[i] for i in min_weight_idx])

            # and remove that edge 
            edge_count[curr_v] -= 1
            edge_weight[curr_v] += 1
            #adj[curr_v].remove(next_v)
            
  
            # Move to next vertex 
            curr_v = next_v 

        # back-track to find remaining circuit 
        else:
            circuit.append(curr_v) 
            
            # Back-tracking 
            curr_v = curr_path[-1]
            curr_path.pop() 

    # we've got the circuit, now print it in reverse 
    directions = [circuit[-1]]
    for i in range(len(circuit) - 1, -1, -1): 
        print(circuit[i], end = "")
        if directions[-1] != circuit[i]:
            directions.append(circuit[i])
        if i: 
            print(" -> ", end = "")
            
            
    return directions


if __name__ == "__main__": 
    
    adj_sion = dict()
        
    for edge1,edge2,connection in sion_zone_1:
        if edge1 not in adj_sion:
            adj_sion.update({edge1:[edge2]})
        else:
            connected_nodes = adj_sion.get(edge1)
            connected_nodes.append(edge2)
            adj_sion.update({edge1 : connected_nodes})
            
        if (connection == 1):
            if edge2 not in adj_sion:
                adj_sion.update({edge2:[edge1]})
            else:
                connected_nodes = adj_sion.get(edge2)
                connected_nodes.append(edge1)
                adj_sion.update({edge2 : connected_nodes})
                    
                    
            
    directions = printCircuit(adj_sion)
    print() # print solution in terms of labels of vertices
  

# xy coordinates of the vertices in EPSG:4326 are stored in the following csv file
coors = pd.read_csv('scan_nodes_XY.csv')

# export the list of coordinates -> copy-paste in a web mapping service such as Google Maps or Bing Maps
with open('directions.txt','w') as f:
    for stop in directions:
        f.write('%f, %f\n' % (coors[coors['id'] == stop]['Y'], coors[coors['id'] == stop]['X']))
            

