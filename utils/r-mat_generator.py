from scipy import rand
import snap
import pandas as pd
import numpy as np
import networkx as nx
import random
import matplotlib.pyplot as plt

Rnd = snap.TRnd()
Graph = snap.GenRMat(1000, 2000, .5, .2, .17, Rnd)
data = [[EI.GetSrcNId(), EI.GetDstNId()] for EI in Graph.Edges()]
cols = ["Source", "Target"]
df = pd.DataFrame(data[0:], columns=cols)
df[cols] = np.sort(df[cols].values, axis=1)
df = df.drop_duplicates().sort_values(by=cols).reset_index(drop=True)
print(df)
df.to_csv("data/RMAT_dataset.csv", index=False)

G = nx.from_pandas_edgelist(df, "Source", "Target")
nx.draw_networkx(G)
#plt.show()

list_nodes = list(range(0, 1000))

N_insert = 1000
list_insert = []
while len(list_insert) < N_insert:
    s = random.choice(list_nodes)
    d = random.choice(list(filter(lambda ele: ele != s, list_nodes)))

    if ((df["Source"] == s) & (df["Target"] == d)).any():
        list_insert.append([s, d])
        #print(len(list_insert), list_insert)

insert_df = pd.DataFrame(list_insert[0:], columns=cols)
insert_df.to_csv("data/insert.csv", index=False)
