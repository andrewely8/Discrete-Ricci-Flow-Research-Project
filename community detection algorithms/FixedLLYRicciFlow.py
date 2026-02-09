import numpy as np
import graphClass
import graphNetworks
import ot

#Fixed Lin Lu lau Curvature
#Based on "The weighted Forman and Lin-Lu-Yau Ricci flow on graphs" (only the LLY part)

import numpy as np
import graphClass
import graphNetworks
import ot

#gamma function Lin Lu lau Curvature
#Based on 'Ollivier Ricci-flow on weighted graphs'

epsilon = 10**(-3)  #used for limit approximation

def computeMassDistribution(Graph,vertex,adjMatrix,m1,m2):
	neighborSet = adjMatrix[vertex]
	distribution = [0 for _ in range(len(neighborSet))]

	gammaSum = 0
	for i in range(len(neighborSet)):
		if neighborSet[i] != None:
			try:
				gammaSum += gamma(neighborSet[i])
			except: #division by zero
				gammaSum += epsilon

	for i,weight in enumerate(neighborSet):
		if weight != None:
			try:
				distribution[i] = (epsilon * m2[vertex][i])/m1[vertex]
			except: #division by zero
				distribution[i] = (epsilon * m2[vertex][i])/epsilon

	distribution[vertex] = 1 - epsilon * deg(vertex,neighborSet,m1,m2)

	return distribution

def wasserstein(m_u,m_v,costMatrix):
	dist = ot.emd2(m_u,m_v,costMatrix)
	return dist

def computeCurvature(Graph,u,v,edgeWeight,adjMatrix,costMatrix,m1,m2):
	d = costMatrix[u][v]
	m_u = computeMassDistribution(Graph,u,adjMatrix,m1,m2)
	m_v = computeMassDistribution(Graph,v,adjMatrix,m1,m2)
	w = wasserstein(m_u,m_v,costMatrix)
	try:
		kEpsilonCurvature = 1 - (w/d)
	except:
		kEpsilonCurvature = 1 - (w/epsilon)
	curvature = (1/epsilon)*kEpsilonCurvature
	return curvature

def cutEdges(Graph, cutThreshold):
	for edge in Graph.edges[:]: #iterate over a copy of the list
		if edge['weight'] > cutThreshold:
			Graph.removeEdge(edge)
			print('removed edge: ', edge)


#
def deg(x,neighborSet,m1,m2):
	numerator = 0
	for i,weight in enumerate(neighborSet):
		if weight != None:
			numerator+=m2[x][i]
	return numerator/m1[x]


def FixedLLY(Graph,maxIterations,normalize=True):
	
	#vertex 'measures', for now m1 = 1 for all vertices
	m1 = [1 for _ in range(Graph.num_nodes)] 

 	#edge 'measures', for now m2 = 1 for all edges (note we set for non existing edges too, fine for now)
	m2 = [[1 for _ in range (Graph.num_nodes)] for _ in range (Graph.num_nodes)] 

	

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
			edge['curvature'] = computeCurvature(Graph,edge['u'],edge['v'],edge['weight'],adjMatrix,costMatrix,m1,m2)

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
	cutEdges(Graph,0.025) #Since we are using normalized edge weight, small cuttoff
	for edge in Graph.edges:
		print(edge)
		if edge['weight'] < 0:
			edge['weight'] = 0.1 #prevent negative edge weights for display purposes
	Graph.drawGraph(display=True,savePath='testFootballFixedLLY.gexf')


myGraph = graphClass.CurvatureGraph(graphNetworks.football)
FixedLLY(myGraph,maxIterations=1,normalize=True)