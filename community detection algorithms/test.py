import numpy as np
import graphClass
import graphNetworks
import networkx as nx
import ot

myGraph = graphClass.CurvatureGraph(graphNetworks.zacharyKarateClub)
G = myGraph.drawGraph(display=False)
comms = nx.community.louvain_communities(G,resolution=0.5)
groundTruth = [{0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 16, 17, 19, 21}, {9, 14, 15, 18, 20, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32,33}]
colorMap = {}

colors = [
			(255, 0, 0), (0, 0, 255), (0, 0, 0), (0, 255, 0), (1, 255, 254), (255, 166, 254), (255, 219, 102), (0, 100, 1), (1, 0, 103), 
			(149, 0, 58), (0, 125, 181), (255, 0, 246), (255, 238, 232), (119, 77, 0), (144, 251, 146), (0, 118, 255), (213, 255, 0), 
			(255, 147, 126), (106, 130, 108), (255, 2, 157), (254, 137, 0), (122, 71, 130), (126, 45, 210), (133, 169, 0), (255, 0, 86), 
			(164, 36, 0), (0, 174, 126), (104, 61, 59), (189, 198, 255), (38, 52, 0), (189, 211, 147), (0, 185, 23), (158, 0, 142), 
			(0, 21, 68), (194, 140, 159), (255, 116, 163), (1, 208, 255), (0, 71, 84), (229, 111, 254), (120, 130, 49), (14, 76, 161), 
			(145, 208, 203), (190, 153, 112), (150, 138, 232), (187, 136, 0), (67, 0, 44), (222, 255, 116), (0, 255, 198), (255, 229, 2), 
			(98, 14, 0), (0, 143, 156), (152, 255, 82), (117, 68, 177), (181, 0, 255), (0, 255, 120), (255, 110, 65), (0, 95, 57), 
			(107, 104, 130), (95, 173, 78), (167, 87, 64), (165, 255, 210), (255, 177, 103), (0, 155, 255), (232, 94, 190)
		]

for node in myGraph.nodes:
	if node in groundTruth[0]:
		colorMap[node] = '255,0,0'
	else:
		colorMap[node] = '0,0,255'

myGraph.drawGraph(display=True, savePath = 'test.gexf',colorMap=colorMap)

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


