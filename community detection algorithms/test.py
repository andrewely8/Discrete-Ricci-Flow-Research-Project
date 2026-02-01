import numpy as np
import graphClass
import graphNetworks
import networkx as nx
import ot

myGraph = graphClass.CurvatureGraph(graphNetworks.zacharyKarateClub)

G = myGraph.drawGraph(display=False)
comms = nx.community.louvain_communities(G)
print(comms)