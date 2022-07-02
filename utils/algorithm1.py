import igraph as ig
import networkx as nx

class PNSubgraph:
    def __init__(self, N_vertex, Graph):
        self.C_id = []
        self.Size = 0
        self.Level = []
        self.PN = []
        self.Count = []

G = nx.full_rary_tree(3, 5)
def BFS_extract_PN_subgraph(V, E, N_vertex):
    thresh_PN = 6
    C_id = [None] * N_vertex
    PN = []
    size = [0]*N_vertex
    Q = []  
    level = [-1]*len(V)
    count = [0]*len(V)
    for i in range(N_vertex):
        start = 0
        end = 1
        Q.insert(0, V[i])
        level[i] = 0
        C_id[i] = V[i]
        while start!=end:
            stop = end
            j = start
            while j <= end:
                for d in E[Q[j][0]]:
                    if level[d]==-1:
                        Q[end] = d
                        end+=1
                        level[d]=level[Q[j][0]]+1
                        C_id[d]=C_id[Q[j][0]]
                    if count[d] < thresh_PN:
                        if level[Q[j][0]] < level[d]:
                            PN[[d][count[d]]] = Q[j][0]
                            count[d]+=1
                        elif level[Q[j][0]] == level[d]:
                            PN[[[d][count[d]]]] = -Q[j][0]
                            count[d]+=1
            start=stop
        size[i]=end
                        
