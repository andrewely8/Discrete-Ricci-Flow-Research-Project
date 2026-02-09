import numpy as np
import graphClass
import graphNetworks
import ot

#gamma function Lin Lu lau Curvature
#Based on 'Ollivier Ricci-flow on weighted graphs'

epsilon = 10**(-2)  #used for limit approximation
alphaLimit = 1 - epsilon

def computeMassDistribution(Graph,vertex,adjMatrix):
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
				distribution[i] = ((1-alphaLimit)*gamma(weight))/gammaSum
			except: #division by zero
				distribution[i] = ((1-alphaLimit)*epsilon)/gammaSum
	distribution[vertex] = alphaLimit

	return distribution

def wasserstein(m_u,m_v,costMatrix):
	dist = ot.emd2(m_u,m_v,costMatrix)
	return dist

def computeCurvature(Graph,u,v,edgeWeight,adjMatrix,costMatrix):
	d = costMatrix[u][v]
	m_u = computeMassDistribution(Graph,u,adjMatrix)
	m_v = computeMassDistribution(Graph,v,adjMatrix)
	w = wasserstein(m_u,m_v,costMatrix)
	try:
		kAlphaCurvature = 1 - (w/d)
	except:
		kAlphaCurvature = 1 - (w/epsilon)
	curvature = kAlphaCurvature/(1-alphaLimit)
	return curvature

def cutEdges(Graph, cutThreshold):
	for edge in Graph.edges[:]: #iterate over a copy of the list
		if edge['weight'] > cutThreshold:
			Graph.removeEdge(edge)
			print('removed edge: ', edge)


#gamma(x) = 1/x 
def gamma(x):
	return 1/x


def GammaLLY(Graph,maxIterations,normalize=True):
	
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
	Graph.drawGraph(display=True,savePath='testFootballGammaLLY.gexf')


myGraph = graphClass.CurvatureGraph(graphNetworks.football)
GammaLLY(myGraph,maxIterations=10,normalize=False)