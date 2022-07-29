import streamlit as st

st.title('A New Parallel Algorithm for Connected Components in Dynamic Graphs')
from multiprocessing import Process
import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config

import testStreamlit as p
st.sidebar.title("Controls")

OPTIONS = st.radio(
     "OPERATION :",
     ('INSERT', 'DELETE'))
RUN =  st.sidebar.button("RUN")
EDGE_OP = st.text_input("Edge ")

from random import randint

color = []
n = 2000

for i in range(n):
    color.append('#%06X' % randint(0, 0xFFFFFF))

state = st.session_state

def visualization(G):
     Source_Connect = G.Edges.keys()
     Target_Connect = G.Edges.values()
        
        
     config = Config(width=700,
                height=700,
                directed=False,
                nodeHighlightBehavior=True,
                #highlightColor="#F7A7A6",  # or "blue"
                highlightColor= color[randint(0,100)],
                collapsible=True,
                node={'labelProperty': 'label'},
                link={'labelProperty': 'label', 'renderLabel': True}
                # **kwargs e.g. node_size=1000 or node_color="blue"
                )

     nodes = []
     for node in range(len(G.Vertex)):
         nodes.append(Node(id=str(G.Vertex[node]),
                          label=str(G.Vertex[node]),
                          size=300,
                          color=color[int(G.C_id[G.Vertex[node]])]
                         ))
        
     edges = []
     for connect in G.Edges:
          for tmp in G.Edges[connect]:
           tmp_color = "#FEEF07"
           if tmp in G.PN[connect] or -1* tmp in G.PN[connect] or connect in G.PN[tmp] or -1*connect in G.PN[tmp]:
              tmp_color = "#EE072A"
           edges.append(Edge(source=str(connect),

                       target=str(tmp),
                       color = tmp_color
                      )
                 ) 
        
     agraph(nodes=nodes,
                      edges=edges,
                      config =config
                     )
G =  p.PNSubgraph(2,"D:\Zoom_HK3_2021\Graph mining\Final Seminar\primaryschool.csv")
G.BFS_extract_PN_subgraph(2,G.Vertex,1)
visualization(G)
if __name__ == '__main__':
 
   if RUN :
     S_D = EDGE_OP.split(" ")
     op_sd = []
     for ed in range(len(S_D)):
        tmp = []
        tmp.append(int(S_D[ed]))
        tmp.append(int(S_D[ed+1]))
        ed +=2
        op_sd.append(tmp) 
        if ed >= len(S_D) :
             break
     
     if OPTIONS == "INSERT":
        G.Insert_Connect(op_sd)
     if OPTIONS == "DELETE":
        G.Delete_Connect(op_sd)
     print(G.PN)
     print(G.Edges)
     visualization(G)
     

