import igraph as ig
import networkx as nx
inf = float('inf')
class PNSubgraph:
    def __init__(self, N_vertex, thresh_PN):
        self.C_id = [None]*N_vertex
        self.Size = 0
        self.Level = [inf]*N_vertex
        self.PN = [inf]*thresh_PN
        self.Count = [0]*N_vertex

G = nx.graph()
def BFS_extract_PN_subgraph(V, E, N_vertex):
    thresh_PN = 2
    res = PNSubgraph()

                        
