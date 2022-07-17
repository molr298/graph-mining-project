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
from multiprocessing import Pool
import multiprocessing

class PNSubgraph:
    def __init__(self, thresh_PN, input_file):
        # input file is a csv file, with source and target vertex - not dupplicate
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

    def parallel_(self, i, Q, end, thresh_PN, thread):
        for d in self.Edges[i]:
            print(i, d, self.Edges[i])
            print(self.PN.values())
            print(self.Level)
            print(self.Count)
            print(f"__________{end}______________")
            if self.Level[d] == self.N_vertex*2:
                Q.append(d)
                self.Level[d] = self.Level[i]+1
                self.C_id[d]=self.C_id[i]
                end+=1
            if self.Count[d]<thresh_PN:
                if self.Level[i]!=self.Level[d]:
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

    def BFS_extract_PN_subgraph(self, thresh_PN):
        
        for v in self.Vertex:
            Q = []
            Q_below = []
            N_Q = len(Q)
            if self.Level[v] == self.N_vertex*2:
                start = 0
                end = 1
                Q.insert(0, v)
                self.Level[v] = 0
                self.C_id[v] = v
                threads_ = []
                while Q!=[]: 
                            
                    #           
                    # 
                    
                    #print()
                    for thread in range(len(Q)):
                        t = Thread(
                            target = self.parallel_,
                            args = (Q[thread], Q, end, thresh_PN, thread, )
                        )
                        t.daemon = True
                        t.start()
                        threads_.append(t)
                    for t in threads_:
                        t.join()
                self.Size[v]=end
        

    def updateInsert(self,ALLconnect_S_D):
            Source = ALLconnect_S_D[0]
            Destination = ALLconnect_S_D[1]
            if Source in self.Vertex:   
             if self.C_id[Source] == self.C_id[Destination] :
                if self.Level[Source] > 0 :
                     if self.Level[Destination] < 0 : 
                        if self.Level[Source] < - self.Level[Destination] :
                            if self.Count[Destination] < 2 :
                                self.PN[Destination].append(Source)
                                self.Count[Destination]+=1
                            else:
                                self.PN[Destination][0] = Source
                            self.Level[Destination] = - self.Level[Destination]
                     else :
                        if self.Count[Destination] < 2 :
                                if self.Level[Source] < self.Level[Destination]:
                                    self.PN[Destination].append(Source)
                                    self.Count[Destination] +=1
                                elif self.Level[Source] == self.Level[Destination]:
                                    self.PN[Destination].append("-"+Source)
                                    self.Cound[Destination]+=1
                        elif self.Level[Source] < self.Level[Destination]:
                          for i in range(2):
                             if self.PN[Destination][i] < 0 :
                                    self.PN[Destination][i] = Source
                                    break
                     
            
            

    def Insert_Connect(self):
            agents = 5
            chunksize = 3
            connect_S_D=[[13,11],[9,12],[7,8]]
            multiprocessing.freeze_support()
           
            # with Pool(processes=agents) as pool:
            #    result_Pool = pool.map(self.updateInsert, connect_S_D,3)
            #    result_Pool
            for i in connect_S_D :
                if i[0] in self.Vertex:
                 id_Souce = self.C_id[i[0]]
                 id_Destination = self.C_id[i[1]]
                 if self.Size[self.C_id[id_Souce]] == 1:
                    self.Size[self.C_id[id_Souce]] == 0 
                    self.Size[self.C_id[id_Destination]] +=1
                    self.C_id[i[0]] = self.C_id[i[1]]
                    self.PN[i[0]] = [i[1]]
                    self.Level[i[0]] = self.Level[i[1]] + 1
                    self.Count[i[0]]  = 1
                else:
                    self.Level[connect_S_D[i][0]] = self.Level[connect_S_D[i][1]] + 1  
    
if __name__ ==  '__main__':
 G = PNSubgraph(2, 'primaryschool.csv')     
 G.BFS_extract_PN_subgraph(2)
 
 G.Insert_Connect()
 