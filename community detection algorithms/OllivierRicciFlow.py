import numpy as np
import graphClass
import graphNetworks
import ot

#Ollivier Curvature
#based on 'SUPPLEMENTARY_Community Detection on Network with Ricci Flow'

def computeMassDistribution(Graph,vertex,adjMatrix,alpha=0.5,p=2):
	neighborSet = adjMatrix[vertex]
	distribution = [0 for _ in range(len(neighborSet))]

	C = 0
	for i in range(len(neighborSet)):
		if neighborSet[i] != None:
			C += np.exp(-1*((Graph.shortestPath(vertex,i,adjMatrix))**p))

	for i,weight in enumerate(neighborSet):
		if weight != None:
			distribution[i] = ((1-alpha)/C) * np.exp(-1*((Graph.shortestPath(vertex,i,adjMatrix))**p))
	distribution[vertex] = alpha 

	return distribution

def wasserstein(m_u,m_v,costMatrix):
	dist = ot.emd2(m_u,m_v,costMatrix)
	return dist

def computeCurvature(Graph,u,v,edgeWeight,adjMatrix,costMatrix):
	d = Graph.shortestPath(u,v,adjMatrix)
	d = costMatrix[u][v]
	m_u = computeMassDistribution(Graph,u,adjMatrix)
	m_v = computeMassDistribution(Graph,v,adjMatrix)
	w = wasserstein(m_u,m_v,costMatrix)
	curvature = 1 - (w/d)
	return curvature

def cutEdges(Graph, cutThreshold):
	for edge in Graph.edges[:]: #iterate over a copy of the list
		if edge['weight'] > cutThreshold:
			Graph.removeEdge(edge)
			print('removed edge: ', edge)

def Ollivier(Graph,maxIterations,normalize=True):
	
	if normalize: #normalize at t=0 before flow evolution
		totalWeight = 0
		for edge in Graph.edges:
			totalWeight += edge['weight']
		for edge in Graph.edges:
			edge['weight'] = edge['weight']/totalWeight

	for iteration in range(maxIterations):
		adjMatrix = Graph.getAdjacencyMatrix()
		costMatrix = Graph.getCostMatrix(adjMatrix)
		for edge in Graph.edges:
			edge['curvature'] = computeCurvature(Graph,edge['u'],edge['v'],edge['weight'],adjMatrix,costMatrix)

		if normalize:
			norm = 0
			for edge in Graph.edges:
				norm += edge['weight']*edge['curvature']
			for edge in Graph.edges:
				edge['weight'] = edge['weight'] + -1*edge['curvature']*edge['weight'] + edge['weight']*norm

		elif not normalize:
			for edge in Graph.edges:
				edge['weight'] = edge['weight'] + -1*edge['curvature']*edge['weight']


	#Display results and end graph
	for edge in Graph.edges:
		print(edge)
	cutEdges(Graph,2)
	for edge in Graph.edges:
		print(edge)
	Graph.drawGraph(display=True,savePath='testFootballOllivierW4.gexf')


myGraph = graphClass.CurvatureGraph(graphNetworks.football)
Ollivier(myGraph,maxIterations=50,normalize=False)


