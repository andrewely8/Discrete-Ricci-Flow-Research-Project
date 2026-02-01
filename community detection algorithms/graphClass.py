'''
This file contains a custom graph object to construct a graph that supports curvature usage and drawing/saving the graph.
'''
import networkx as nx
import numpy as np
import heapq
import matplotlib.pyplot as plt

class CurvatureGraph(object):

	def __init__(self, edgeSet):
		self.edges = self.addEdgesFrom(edgeSet)
		self.nodes = self.addNodesFrom(edgeSet)
		self.G = (self.nodes,self.edges)
		self.num_nodes = len(self.nodes)

	def addEdgesFrom(self,edgeSet):
		edges = []
		for edge in edgeSet:
			edges.append({'u': edge[0], 'v': edge[1], 'weight': edge[2], 'curvature': None})
		return edges

	def addNodesFrom(self,edgeSet):
		nodes = set() #avoid duplicate nodes
		for edge in edgeSet:
			nodes.add(edge[0])
			nodes.add(edge[1])
		return list(nodes)

	def removeEdge(self,edge):
		self.edges.remove(edge)

	def updateEdgeWeight(self,u,v,newWeight):
		for edge in self.edges: #check if the specified u,v exists
			if edge['u'] == u and edge['v'] == v:
				edge['weight'] = newWeight
				return 0
		print(f"edge ({u},{v}) does not exist")

	def updateEdgeCurvature(self,u,v,newCurvature):
		for edge in self.edges: #check if the specified u,v exists
			if edge['u'] == u and edge['v'] == v:
				edge['curvature'] = newCurvature
				return 0
		print(f"edge ({u},{v}) does not exist")

	def getEdgeWeight(self,u,v):
		for edge in self.edges: #check if the specified u,v exists
			if (edge['u'] == u and edge['v'] == v) or (edge['u'] == v and edge['v'] == u):
				return edge['weight']
		print(f"edge ({u},{v}) does not exist")

	def getEdgeCurvature(self,u,v):
		for edge in self.edges: #check if the specified u,v exists
			if (edge['u'] == u and edge['v'] == v) or (edge['u'] == v and edge['v'] == u):
				return edge['curvature']
		print(f"edge ({u},{v}) does not exist")

	def getCostMatrix(self,adjMatrix):
		costMatrix = [[None for _ in range (self.num_nodes)] for _ in range (self.num_nodes)]

		for i in range(len(costMatrix)):
			for j in range(len(costMatrix[i])):
				costMatrix[i][j] = self.shortestPath(i,j,adjMatrix)

		return costMatrix


	def shortestPath(self, src, target, adjMatrix):
		pq = []
		dist = [np.inf] * self.num_nodes
		dist[src] = 0.0
		heapq.heappush(pq, (0.0, src))

		while pq:
			d, u = heapq.heappop(pq)
			if d > dist[u]:
				continue
			if u == target:
				return dist[target]

			row = adjMatrix[u]
			for v, w in enumerate(row):
				if w is None:
					continue
				nd = dist[u] + w
				if nd < dist[v]:
					dist[v] = nd
					heapq.heappush(pq, (nd, v))

		return dist[target]


	def getAdjacencyMatrix(self):
		adj = [[None for _ in range (self.num_nodes)] for _ in range (self.num_nodes)]
		for edge in self.edges:
			adj[edge['u']][edge['v']] = edge['weight']
			adj[edge['v']][edge['u']] = edge['weight'] #edges are undirected, include both ways
		return adj



	def drawGraph(self,display=True,savePath=None):
		nxGraph = nx.Graph()
		nxGraph.add_nodes_from(self.nodes)

		for edge in self.edges:
				if round(edge['weight'],2) == 0:
					edge['weight'] = 0.1 #ensure near zero edge weights aren't rounded to 0
				if edge['curvature'] == None:
					edge['curvature'] = 0 #In case we are drawing a graph with no curvature defined (we did not do Ricci Flow on it)
				edge_label = f"(w={round(edge['weight'],2)},k={round(edge['curvature'],2)})"
				nxGraph.add_edge(edge['u'],edge['v'],weight=round(edge['weight'],2),curvature=round(edge['curvature'],2),label=edge_label)
		pos = nx.spring_layout(nxGraph)
		nx.draw_networkx_nodes(nxGraph, pos, node_size=500)
		nx.draw_networkx_labels(nxGraph, pos, font_size=10, font_family="sans-serif")

		negEdges = [(u, v) for (u, v, d) in nxGraph.edges(data=True) if d["curvature"] < -0.1]
		neutralEdges = [(u, v) for (u, v, d) in nxGraph.edges(data=True) if d["curvature"] >= -0.1 and d["curvature"] <= 0.1]
		posEdges = [(u, v) for (u, v, d) in nxGraph.edges(data=True) if d["curvature"] > 0.1]

		nx.draw_networkx_edges(nxGraph, pos, edgelist=negEdges, width=1, alpha=0.5, edge_color="red")
		nx.draw_networkx_edges(nxGraph, pos, edgelist=neutralEdges, width=1, alpha=0.5, edge_color="black")
		nx.draw_networkx_edges(nxGraph, pos, edgelist=posEdges, width=1, alpha=0.5, edge_color="skyblue")

		edge_weight_labels = nx.get_edge_attributes(nxGraph, 'label')
		edge_curvature_labels = nx.get_edge_attributes(nxGraph, "curvature")
		nx.draw_networkx_edge_labels(nxGraph, pos, edge_curvature_labels,font_size=8)
		nx.draw_networkx_edge_labels(nxGraph, pos, edge_weight_labels,font_size=8)
		
		if savePath:
			nx.write_gexf(nxGraph,savePath)
		if display:
			plt.show()

		return(nxGraph) #if we want the networkX data structure.

