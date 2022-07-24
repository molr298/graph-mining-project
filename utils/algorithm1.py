import igraph as ig
import networkx as nx
import ast
import pandas as pd
from collections import defaultdict
from joblib import Parallel, delayed, parallel_backend
from datetime import datetime
from threading import Thread, Barrier
import time
inf = float('inf')
class PNSubgraph:
    def __init__(self, thresh_PN, input_file):
        # input file is a csv file, with source and target vertex - not dupplicate
        self.thresh_PN = thresh_PN
        df = pd.read_csv(input_file)
        self.Vertex = pd.unique(df[['Source', 'Target']].values.ravel('k'))
        connection = df.values.tolist()
        self.Edges = defaultdict(list)
        for c in connection:
            self.Edges[c[0]].append(c[1])
            self.Edges[c[1]].append(c[0])

        self.N_vertex = len(self.Vertex)
        self.Level = dict.fromkeys(self.Vertex, self.N_vertex*2)
        self.Count = dict.fromkeys(self.Vertex, 0)
        self.C_id = dict.fromkeys(self.Vertex, 0)
        self.Size = dict.fromkeys(self.Vertex, 0)
        self.PN = defaultdict(list)
        for v in self.Vertex:
            self.PN[v].append(None)
            self.PN[v].append(None)
        print(self.PN)
        self.neighbor = dict(zip(self.Vertex, self.Edges))

    def BFS(self, i, Q, end, thresh_PN, thread):
        time.sleep(0.0001)
        for d in self.Edges[i]:
            if self.Level[d] == self.N_vertex*2:
                Q.append(d)
                self.Level[d] = self.Level[i]+1
                self.C_id[d]=self.C_id[i]
                end+=1
            if self.Count[d]<thresh_PN:
                if self.Level[i]<self.Level[d]:
                    self.PN[d][self.Count[d]]=i
                    self.Count[d]+=1
                elif self.Level[i]==self.Level[d]:
                    self.PN[d][self.Count[d]]=-i
                    self.Count[d]+=1
        Q = Q.remove(i)

    def LOG(self):
        now = datetime.now()
        dt_string = now.strftime("%H-%M-%S")
        filename = "result/"+dt_string+"-RESULT.log"
        f = open(filename, "a")
        f.write(str(self.PN))
        f.close()

    def BFS_extract_PN_subgraph(self):
        print(self.Edges)
        for v in self.Vertex:
            Q = []
            if self.Level[v] == self.N_vertex*2:
                end = 1
                Q.insert(0, v)
                self.Level[v] = 0
                self.C_id[v] = v
                threads_ = []
                while Q!=[]: 
                    #print()
                    for thread in range(len(Q)):
                        t = Thread(
                            target = self.BFS,
                            args = (Q[thread], Q, end, self.thresh_PN, thread, )
                        )
                        t.daemon = True
                        t.start()
                        threads_.append(t)
                    for t in threads_:
                        t.join()
                self.Size[v]=end
        print(self.PN)
        print(self.C_id)
    
    def reset_vertex(self, list_of_vertex):
        for v in list_of_vertex:
            self.Level[v] = self.N_vertex*2
            self.Count[v] = 0
            for i in range(self.thresh_PN):
                self.PN[v][i] = None
    
    def Connect_component(self, source, target):
        list_of_vertex = [k for k, v in self.C_id.items() if v == self.C_id[target]]
        self.reset_vertex(list_of_vertex)
        self.C_id[target] = self.C_id[source]
        self.Edges[target].append(source)
        self.Edges[source].append(target)
        Q = [source]
        end =1
        self.Level[target] = self.Level[source]+1
        threads_=[]
        start = 0
        stop = 1
        while start!=stop:
            stop = end
            for i in Q:
                for d in self.Edges[i]:
                    if self.Level[d] == self.N_vertex*2:
                        Q.append(d)
                        self.Level[d] = self.Level[i]+1
                        self.C_id[d]=self.C_id[i]
                        end+=1
                    if self.Count[d]<self.thresh_PN:
                        if self.Level[i]<self.Level[d]:
                            self.PN[d][self.Count[d]]=i
                            self.Count[d]+=1
                        elif self.Level[i]==self.Level[d]:
                            self.PN[d][self.Count[d]]=-i
                            self.Count[d]+=1
            start=stop            
                
        
    def connect_in_same_component(self, S_D, thread):
        Source = S_D[0]
        Target = S_D[1]
        if self.C_id[Source] == self.C_id[Target]:
            if self.Level[Source] > 0:
                if self.Level[Target] < 0:
                    if (self.Level[Source] < - self.Level[Target]):
                        if self.Count[Target] < self.threshPN:
                            self.PN[Target][self.Count[Target]].append(Source)
                            self.Count[Target]+=1
                        else:
                            self.PN[Target][0] = Source
                        self.Level[Target] = -self.Level[Target]
                else:
                    if self.Count[Target] < self.threshPN:
                        if self.Level[Source] < self.Level[d]:
                            self.PN[Target][self.Count[Target]] = Source
                        elif self.Level[Source] == self.Level[Target]:
                            self.PN[Target][self.Count[Target]] = -Source

                    elif self.Level[Source] < self.Level[Target]:
                        for i in range(0, self.threshPN):
                            if self.PN[Target][i] < 0:
                                self.PN[Target][i] = Source
                                break

    def Insert_Connect(self, list_connection):
        # ALL_level_subgraph - {1:{1:, 2:, 3:levl}, 13:{}}
        # ALL_PN_subgraph - {1:{1:, 2:, 3:PN}, 13:{}}
        threads_ = []
        for thread in range(len(list_connection)):
            t = Thread(
                target = self.connect_in_same_component,
                args = (list_connection[thread], thread, )
            )
            t.daemon = True
            t.start()
            threads_.append(t)
        for t in threads_:
            t.join()
        
        list_connection

        if self.C_id[Source] != self.C_id[Target]:
            if self.Size[Source] == 1:
                self.Size[Target] = 0
                self.Size[Source] += 1
                self.C_id[Target] = Source
                self.PN[Source][0] = Target
                self.Level[Source] = abs(self.Level[Target]) + 1
            else:
                self.Connect_component(Source, Target)



G = PNSubgraph(2, 'primaryschool.csv')     
G.BFS_extract_PN_subgraph()
list_connection = [[7,8], [5, 11], [9, 12], [9, 17]]
G.Insert_Connect(9, 17)
G.LOG()
print(G.C_id)