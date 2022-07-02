from re import L
from time import sleep
from turtle import color
from cv2 import line
from sqlalchemy import false, null, true
import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter
import itertools
from streamlit_agraph import agraph, Node, Edge, Config
from torch import t


#Read source and target
data_ = pd.read_csv("D:\Zoom_HK3_2021\Graph mining\Final Seminar\\primaryschool.csv")

Source = list(data_['Source'].unique())
Target = list(data_['Target'].unique())

data = data_.groupby("Source")["Target"].apply(list).to_dict()

# Set color for each component
colors = ["#FEEF07","D0D313","#EE072A","#0707FE"]

Components = dict()
Num_Components = 1
Component = []
Component.append(data_.iloc[0,0])
Component.append(data_.iloc[0,1])

for node in range(len(data_)) :
    if data_.iloc[node,0] in Component or  data_.iloc[node,1] in Component :
         Component.append(data_.iloc[node,0])
         Component.append(data_.iloc[node,1])
    else :
        Components[Num_Components] = list(set(Component))
        Component= []
        Component.append(data_.iloc[node,0])
        Component.append(data_.iloc[node,1])
        Num_Components+=1
    if node == len(data_) - 1:
         Components[Num_Components] = list(set(Component))

len_column = 17

Level = [0] * len_column
#PN = dict((el,[]) for el in list(range(1,len_column)))
Size = []
threshPN = 2
Distance = []

def PNSubGraph(visited, data, node , PN , threshPN ,queue , Level):
  visited.append(node)
  queue.append(node)
  

  PN[node] = [element *-1 for element in data[node][0:threshPN]]
  Level[node] = 1 
  while queue:
    s = queue.pop(0) 
    print (s, end = " ") 
    
    if s not in list(data.keys()) : 
        break
    
    ##len_pn = len(PN[s])
    
    for neighbour in data[s]:
       if Level[neighbour] == 0 :
          Level[neighbour] = Level[s] + 1
       
       if len(PN[neighbour]) < threshPN :
            if Level[s] < Level[neighbour] :
              if s not in PN[neighbour] : 
               PN[neighbour].append(s)
            if Level[s] == Level[neighbour]:
               
               PN[neighbour].append(-s)
            
       if len(PN[s]) < threshPN :
             PN[s].append(-neighbour)
       queue.append(neighbour)
      

def PN_Sub_Graph_For_Component():
      ALL_PN_SubGraph= dict()
      ALL_Level_SubGraph = dict()
      key_connect = data.keys()
      for component in range(1,Num_Components+1):

           for node in Components[component] :
            if node in key_connect :
             Level = dict((el,0) for el in Components[component]) 
             PN = dict((el,[]) for el in Components[component])
             PNSubGraph([],data,node,PN,threshPN,[],Level)
             
             ALL_PN_SubGraph[component] = PN
             ALL_Level_SubGraph[component] = Level
             break 
      
      return ALL_PN_SubGraph
ALL_PN_SubGraph =  PN_Sub_Graph_For_Component()

def Insert_Connect(Source , Target ):
  Check_Exist_Source = 0
  Check_Exist_Target = 0
  
  for component in range(1,Num_Components+1):
      if Source in Components[component]:
         Check_Exist_Source = component
      if Target in Components[component]:
         Check_Exist_Target = component
  if Check_Exist_Source == Check_Exist_Target :
       #if Level[Source] > 0 :
       return 
  else :
    if Source not in Components.keys() :
      Components[Check_Exist_Target].append(Source)
      ALL_PN_SubGraph[Check_Exist_Target][Source]=[Target]
      Level[Source] = abs(Level[Target]) + 1
             


nodes = []
edges = []

for connect in range(len(data_)) :
    Source_Connect = data_.iloc[connect,0]
    Target_Connect =  data_.iloc[connect,1]
    
    Color_Source = "#FEEF07"
    Color_Target = "#FEEF07"

    for component in range(1,Num_Components) :
              if Source_Connect in Components[component]:
                    Color_Source = colors[component]
              if Target_Connect in Components[component]:
                    Color_Target = colors[component]

    if Source_Connect not in nodes :
       
       nodes.append(Node(id = str(Source_Connect) , 
                       label = str(Source_Connect),
                        size = 300,
                        color= Color_Source ))
       

    if Target_Connect not in nodes :
       nodes.append(Node(id = str(Target_Connect) , 
                       label = str(Target_Connect),
                        size = 300 ,
                         color = Color_Target)) 
    color_edges = colors[3]
    for component in range(1,Num_Components+1) :
        if Source_Connect in Components[component] :
              tmp_a = ALL_PN_SubGraph[component][Source_Connect]
              tmp_b = ALL_PN_SubGraph[component][Target_Connect]
              if Source_Connect in tmp_b or -1*Source_Connect in tmp_b or Target_Connect in tmp_a or -1*Target_Connect in tmp_a :
                     color_edges = colors[2]

    edges.append( Edge(source= str(Source_Connect), 
                   
                   target=str(Target_Connect),
                   color=color_edges
                   ) 
            ) 
config = Config(width=700, 
                height=700, 
                directed= False,
                nodeHighlightBehavior=True, 
                highlightColor="#F7A7A6", # or "blue"
                collapsible=True,
                node={'labelProperty':'label'},
                link={'labelProperty': 'label', 'renderLabel': True}
                # **kwargs e.g. node_size=1000 or node_color="blue"
                ) 

return_value = agraph(nodes=nodes, 
                      edges=edges, 
                      config=config)


nodes.append(Node(id = str(20) , 
                       label = str(20),
                        size = 300,
                        color= "#0707FE" ))
edges.append( Edge(source= str(1), 
                   
                   target=str(20),
                   color=color_edges
                   ) 
            ) 

return_value1 = agraph(nodes=nodes, 
                      edges=edges, 
                      config=config)
# Insert = st.text_input('Insert Source and Target Vertex ')
# if st.button('Insert'):
#       Source = int(Insert[0])
#       Target = int(Insert[2])
    
