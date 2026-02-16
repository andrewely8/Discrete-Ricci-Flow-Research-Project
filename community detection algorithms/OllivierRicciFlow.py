import numpy as np
import graphClass
import graphNetworks
import ot

#Ollivier Curvature
#based on 'SUPPLEMENTARY_Community Detection on Network with Ricci Flow'

epsilon = 10**(-3) #only for division by zero checks

def computeMassDistribution(vertex,adjMatrix,costMatrix,alpha=0.5,p=2):
	neighborSet = adjMatrix[vertex]
	distribution = [0 for _ in range(len(neighborSet))]

	C = 0
	for i in range(len(neighborSet)):
		if neighborSet[i] != None and neighborSet[i] != 0: #any adjacent vertex
			C += np.exp(-1*((costMatrix[vertex][i])**p))

	for i in range(len(neighborSet)):
		if i == vertex: 
			distribution[i] = alpha
		elif neighborSet[i] == None or neighborSet[i] == 0: #not a neighbor
			distribution[i] = 0
		else: #neighbor
			distribution[i] = ((1-alpha)/C) * np.exp(-1*((costMatrix[vertex][i])**p))

	return distribution


def cutEdges(Graph, cutThreshold):
	for edge in Graph.edges[:]: #iterate over a copy of the list
		if edge['weight'] > cutThreshold:
			Graph.removeEdge(edge)
			print('removed edge: ', edge)


def Ollivier(Graph,maxIterations,stepSize = 0.1):
	

	for iteration in range(maxIterations):
		print('iteration -- ', iteration)
		adjMatrix = Graph.getAdjacencyMatrix()
		costMatrix = Graph.getCostMatrix(adjMatrix)

		#Normalize edge weights
		denominator = 0
		for edge in Graph.edges:
			denominator += costMatrix[edge['u']][edge['v']]
		for edge in Graph.edges:
			edge['weight'] = costMatrix[edge['u']][edge['v']] * ((len(Graph.edges))/denominator)

		#recompute cost matrix with normalized edge weights
		adjMatrix = Graph.getAdjacencyMatrix()
		costMatrix = Graph.getCostMatrix(adjMatrix)

		for edge in Graph.edges:
			m_u = computeMassDistribution(edge['u'],adjMatrix,costMatrix)
			m_v = computeMassDistribution(edge['v'],adjMatrix,costMatrix)
			d = costMatrix[edge['u']][edge['v']]
			w = ot.emd2(m_u,m_v,costMatrix)
			#w = ot.sinkhorn2(m_u,m_v,costMatrix,0.1, method='sinkhorn')
			try:
				edge['curvature'] = 1 - (w/d)
			except: #avoid float division by zero
				edge['curvature'] = 1 - (w/epsilon)
			
			edge['weight'] = (costMatrix[edge['u']][edge['v']]) - (stepSize * edge['curvature'] * costMatrix[edge['u']][edge['v']])
			



	#Display results and end graph
	cutEdges(Graph,4)
	for edge in Graph.edges:
		print(edge)

	Graph.drawGraph(display=False,savePath='graphOutputs/test2.gexf')

myGraph = graphClass.CurvatureGraph(graphNetworks.zacharyKarateClub)
Ollivier(myGraph,maxIterations=100,stepSize=1)

