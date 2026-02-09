import numpy as np
import graphClass
import graphNetworks
import networkx as nx
import ot
import sys
import os




# cur_path = os.path.dirname(__file__)
# file_path = os.path.relpath('..\\graph creation tools\\email-Eu-core/email-Eu-core-department-labels.txt', cur_path)
# comms = []

# with open(file_path, 'r') as f:
# 	for line in f:
# 		line = line.strip()
# 		line = line.split(' ')
# 		node = int(line[0])
# 		community = int(line[1])
# 		colorAssignIndex = community % len(colors)
# 		colorAssingTuple = colors[colorAssignIndex]
# 		color = f"{colorAssingTuple[0]},{colorAssingTuple[1]},{colorAssingTuple[2]}"
# 		colorMap[node] = color

# G = myGraph.drawGraph(display=False)
# comms = nx.community.louvain_communities(G,resolution=0.5)
# # groundTruth = [{0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 16, 17, 19, 21}, {9, 14, 15, 18, 20, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32,33}]

myGraph = graphClass.CurvatureGraph(graphNetworks.football)
G = myGraph.drawGraph(display=False, savePath = 'footballOriginal.gexf')
comms = nx.community.louvain_communities(G,resolution=1.0)
print(comms)
print(len(comms))
toDelete = []

for edge in myGraph.edges:
	for i,com in enumerate(comms):
		if edge['u'] in com:
			u_com = i
		if edge['v'] in com:
			v_com = i
	if u_com != v_com:
		toDelete.append(edge)

for edge in toDelete:
	myGraph.removeEdge(edge)


myGraph.drawGraph(display=False, savePath = 'louvainTest.gexf')