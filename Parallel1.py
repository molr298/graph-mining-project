from time import sleep
import igraph as ig
import networkx as nx
import ast
import pandas as pd
from collections import defaultdict
from joblib import Parallel, delayed, parallel_backend
from datetime import datetime
from threading import Thread, Barrier


from sqlalchemy import false, null, true
from zmq import has
inf = float('inf')
from multiprocessing import Pool
import multiprocessing

class PNSubgraph:
    def __init__(self, thresh_PN, input_file):
        # input file is a csv file, with source and target vertex - not dupplicate
        df = pd.read_csv(input_file)
        self.Vertex = []
        for i in range(len(df)):
            Source = df['Source'][i]
            Target = df['Target'][i]
            if Source not in self.Vertex:
                self.Vertex.append(Source)
            if Target not in self.Vertex:
                self.Vertex.append(Target)
            

        connection = df.values.tolist()
        self.Edges = defaultdict(list)
        for c in connection:
            self.Edges[c[0]].append(c[1])
           

        self.N_vertex = len(self.Vertex)
        self.Level = dict.fromkeys(self.Vertex, self.N_vertex*2)
        self.Count = dict.fromkeys(self.Vertex, 0)
        self.C_id = dict.fromkeys(self.Vertex, 0)
        self.Size = dict.fromkeys(self.Vertex, 0)
        self.PN = defaultdict(list)
        for v in self.Vertex:
            self.PN[v].append(None)
            self.PN[v].append(None)
       
        self.neighbor = dict(zip(self.Vertex, self.Edges))

    def parallel_(self, i, Q, end, thresh_PN, thread):
        
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
                elif self.Level[i]==self.Level[d] :
                    self.PN[d][self.Count[d]]=-i
                    self.Count[d]+=1
            if self.Count[i] < thresh_PN :     
                self.PN[i][self.Count[i]]=-d
                self.Count[i]+=1
        sleep(1)
        Q = Q.remove(i)


    def LOG(self):
        now = datetime.now()
        dt_string = now.strftime("%H-%M-%S")
        filename = "result/"+dt_string+"-RESULT.log"
        f = open(filename, "a")
        f.write(str(self.PN))
        f.close()

    def BFS_extract_PN_subgraph(self, thresh_PN , Array_Vertex , Level_Default):
        
        for v in Array_Vertex:
            
            Q = []
            Q_below = []
            N_Q = len(Q)
            if self.Level[v] == self.N_vertex*2:
                start = 0
                end = 1
                Q.insert(0, v)
                self.Level[v] = Level_Default
                self.C_id[v] = v
                threads_ = []
                while Q!=[]: 
                            
                    for threadQ in Q:
                        t = Thread(
                            target = self.parallel_,
                            args = (threadQ, Q, end, thresh_PN, 1, )
                        )
                        t.daemon = True
                        t.start()
                        threads_.append(t)
                        end+=1
                    for t in threads_:
                        t.join()
                    #end+= len(Q)
                self.Size[v]=end - 1
                    
                 
        

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
                                    self.Level[Destination] = self.Level[Source]+1
                                    break
             return self.PN , self.Level , self.Count , ALLconnect_S_D     
            return null
            
            

    def Insert_Connect(self):
            agents = 5
            chunksize = 3
            connect_S_D=[[5,13]]
            multiprocessing.freeze_support()
            Same_Component = []
            Diff_Component = []
            for connect in connect_S_D:
                if self.C_id[connect[0]] == self.C_id[connect[1]]:
                    Same_Component.append(connect)
                else :
                    Diff_Component.append(connect)
            if len(Same_Component) > 0 :
             with Pool(processes=agents) as pool:
               result_Pool = pool.map(self.updateInsert, Same_Component,3)
               if result_Pool != null:
                 self.PN = result_Pool[-1][0]
                 self.Level = result_Pool[-1][1]
                 self.Count = result_Pool[-1][2]
                 Connect_S_D = result_Pool[-1][3]
            
            for i in Diff_Component :
                if i[0] in self.Vertex:
                 id_Souce = self.C_id[i[0]]
                 id_Destination = self.C_id[i[1]]
                 if id_Souce != id_Destination:
                    if self.Size[self.C_id[i[0]]] == 1:
                        self.Size[self.C_id[i[0]]] = 0 
                        self.Size[self.C_id[i[0]]]+=1
                        self.C_id[i[0]] = id_Destination
                        self.PN[i[0]] = i[1]
                        self.Level[i[0]] = abs(self.Level[i[1]]) + 1  
                        self.Count[i[0]] = 1
                    else:
                     if self.Size[self.C_id[i[0]]] > self.Size[self.C_id[i[1]]]:
                        Source =   i[0]
                        Destination = i[1]
                     else:
                        Source =   i[1]
                        Destination = i[0]
                     tmp_Source = Source
                     Vertex_BFS = [k for k, v in self.C_id.items() if v == self.C_id[Destination]]
                     Vertex_Source = [k for k, v in self.C_id.items() if v == self.C_id[Source]]
                     
                     for vertex in self.Vertex:
                        if self.C_id[vertex] == self.C_id[Destination]:
                         if vertex == Destination:
                            self.PN[vertex] = [Source,None]
                            self.Count[vertex] = 1
                         else:
                            self.PN[vertex] = [None,None]
                            self.Count[vertex] = 0
                        


                     self.Level.update(dict(zip(Vertex_BFS,[self.N_vertex*2]*len(Vertex_BFS))))
                     
                     self.BFS_extract_PN_subgraph(2,Vertex_BFS,self.Level[Source]+1)

                     self.Size[self.C_id[Source]]= len(Vertex_BFS)+len(Vertex_Source)
                     self.Size[Destination] = 0
                     self.C_id.update(dict(zip(Vertex_BFS,[self.C_id[Source]]*len(Vertex_BFS))))
                     
    def Do_Delete_Parallel1(self,delete_s_d):
        Source = delete_s_d[0]
        Destination = delete_s_d[1]
        hasParent = False
        for p in range(0,self.Count[Destination]):
            if self.PN[Destination][p] == Source or self.PN[Destination][p] == -Source:
                self.Count[Destination] -=1
                self.PN[Destination][p] = None
                
                #self.PN[Destination][p] = self.PN[Destination][self.Count[Destination]]
            if hasParent == False and self.PN[Destination][p] != None:
                   
             if self.PN[Destination][p] > 0:
                hasParent = True
        

        if hasParent == False and self.Level[Destination] > 0 :
            self.Level[Destination] = -self.Level[Destination]
        self.PN[Destination] = list(set(self.PN[Destination]))    
        return delete_s_d , self.PN , self.Level , self.Count

    def Do_Delete_Parallel2(self,delete_s_d):
        
        Source = delete_s_d[0]
        Destination = delete_s_d[1]
        for p in self.PN[Destination]:
            # if p >= 0 or self.Level[abs(p)] > 0 :
               if p != None :
                if p >= 0:  
                  return 
        return delete_s_d
    
    def parallel_repair_delete(self, i , Q ,end, thresh_PN , Source , Destination , disconnected , SLQ , SLQ_end):
        for neigh in self.Edges[i]:
            if self.C_id[neigh] == self.C_id[Source] :
                if self.Level[neigh] <= abs(self.Level[Destination]) :
                    self.C_id[neigh] = self.C_id[Destination]
                    disconnected = False
                    SLQ[SLQ_end] = neigh
                    SLQ_end = SLQ_end + 1
                else :
                    self.C_id[neigh] = self.C_id[Destination]
                    self.Count[neigh] = 0 
                    self.Level[neigh] = self.Level[i] + 1
                    Q.append(neigh)
                    end+=1
            if self.Count[neigh] < thresh_PN :
                if self.Level[i] < self.Level[neigh] :
                    self.PN[neigh][self.Count[neigh]] = i
                    self.Count[neigh] = self.Count[neigh] + 1
                elif self.Level[i] == self.Level[neigh] :
                    self.PN[neigh][self.Count[neigh]] = -i
                    self.Count[neigh] = self.Count[neigh] + 1

    def parallel_repair_delete1(self,i,Source):
        self.C_id[i] = self.C_id[Source]
    
    def parallel_repair_delete2(self,i,SLQ,SLQ_end,thresh_PN,Destination):
        for neigh in self.Edges[i]:
            if self.C_id[neigh] == self.C_id[Destination]:
                self.C_id[neigh] = self.C_id[i]
                self.Count[neigh] = 0
                self.Level[neigh] = self.Level[i] + 1
                SLQ.append(neigh)
                SLQ_end += 1
            if self.Count[neigh] < thresh_PN :
                if self.Level[i] < self.Level[neigh]:
                    self.PN[neigh][self.Count[neigh]] = i
                    self.Count[neigh] +=1
                elif self.Level[neigh] == self.Level[neigh]:
                    self.PN[neigh][self.Count[neigh]] = -i
                    self.Count[neigh] +=1



    def Repair_Delete_Algorithm(self,Source , Destination , thresh_PN):
        Q = [Destination]
        start = 0 
        end = 1

        SLQ = []
        SLQ_start = 0 
        SLQ_end = 0

        self.Level[Destination] = 0 
        self.C_id[Destination] = Destination
        disconnected = True

        threads_ = []
        while Q!=[]: 
                            
            for threadQ in Q:
                        t = Thread(
                            target = self.parallel_repair_delete,
                            args = (threadQ, Q ,end, thresh_PN , Source , Destination , disconnected , SLQ , SLQ_end, )
                        )
                        t.daemon = True
                        t.start()
                        threads_.append(t)
            for t in threads_:
                        t.join()
            end+= len(Q)
        if disconnected :
            self.Size[Destination] = end
        else:
            for SLQ_thread in SLQ :
                t = Thread(
                            target = self.parallel_repair_delete2,
                            args = (SLQ_thread, Source, )
                        )
                t.daemon = True
                t.start()
                threads_.append(t)
            for t in threads_:
                        t.join()
            while SLQ !=[]:
                for threadQ in Q:
                        t = Thread(
                            target = self.parallel_repair_delete3,
                            args = (threadQ,SLQ,SLQ_end,thresh_PN,Destination,)
                        )
                        t.daemon = True
                        t.start()
                        threads_.append(t)
                for t in threads_:
                        t.join()



            
   

    def Delete_Connect(self,thresh_PN):
        agents = 5
        chunksize = 3
        Delete_S_D=[[6,9]]
        multiprocessing.freeze_support()
        if len(Delete_S_D) > 0 :
         with Pool(processes=agents) as pool:
            result_Pool = pool.map(self.Do_Delete_Parallel1,Delete_S_D,10)
            if result_Pool != null:
                 self.PN = result_Pool[-1][1]
                 self.Level = result_Pool[-1][2]
                 self.Count = result_Pool[-1][3]
        
        result_Pool = []
        if len(Delete_S_D) > 0 :
         with Pool(processes=agents) as pool:
            result_Pool = pool.map(self.Do_Delete_Parallel2,Delete_S_D,3)
            
        print(result_Pool)
        PREV = self.C_id.copy()
        if result_Pool != [None] :
         for delete_e in result_Pool : 
            Source = delete_e[0][0]
            Destination = delete_e[0][1]
            unsafe = (self.C_id[Source] == self.C_id[Destination] == PREV[Source])
            print(unsafe)
            for p in self.PN[Destination]:
                if p >= 0 or self.Level[abs(p)] > 0 :
                    unsafe = False
            print(unsafe)
            # if unsafe :
            #     self.Repair_Delete_Algorithm(Source,Destination,thresh_PN)
                

       
    
if __name__ ==  '__main__':
 G = PNSubgraph(2, 'primaryschool.csv')
    
 G.BFS_extract_PN_subgraph(2,G.Vertex,0)
 print(G.PN)  
 G.Delete_Connect(2) 
 print(G.PN)
 print(G.Count)
 print(G.Size)
 
 