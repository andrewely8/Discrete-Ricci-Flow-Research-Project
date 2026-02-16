import os
import numpy as np
import graphClass
import graphNetworks
import networkx as nx
import ot
import sys
from prettytable import PrettyTable

# triangle with 1 more edge
# graphInput = [(0, 1, 1), (0, 2, 1), (1, 2, 1), (2, 3, 1),]

# complete 3-graph
#graphInput = [(0, 1, 1), (0, 2, 1), (1, 2, 1),]

# complete 4-graph
#graphInput = [(0, 1, 1), (0, 2, 1), (0, 3, 1), (1, 2, 1), (2, 3, 1),(1, 3, 1),]
#graphInput = [(0, 1, 1), (0, 2, 1), (0, 3, 1), (1, 2, 1), (2, 3, 1),(1, 3, 1),(3,4,1)]

# complete 5-graph
# graphInput = [(0, 1, 1), (0, 2, 1), (0, 3, 1), (0, 4, 1), (1, 2, 1), (1, 3, 1), (1, 4, 1), (2, 3, 1), (2, 4, 1), (3, 4, 1)]

# complete 6-graph
graphInput = [(0,1,1), (0,2,1), (0,3,1), (0,4,1), (0,5,1), (1,2,1), (1,3,1), (1,4,1), (1,5,1), (2,3,1), (2,4,1), (2,5,1), (3,4,1), (3,5,1), (4,5,1),]



epsilon = 10**(-3)

# gamma(x) = x  for now.
def gamma(x):
	return 1/x

def computeMassDistribution(vertex,adjMatrix,alpha=0):
	neighborSet = adjMatrix[vertex]
	distribution = [0 for _ in range(len(neighborSet))]
	sumAdjacentGammaWeights = 0

	for i in range(len(neighborSet)):
		if neighborSet[i] != None and neighborSet[i] != 0: #any adjacent vertex
			sumAdjacentGammaWeights += gamma(neighborSet[i])

	for i in range(len(neighborSet)):
		if i == vertex: 
			distribution[i] = alpha
		elif neighborSet[i] == None: #not a neighbor
			distribution[i] = 0
		else: #neighbor
			distribution[i] = ((1-alpha)*gamma(neighborSet[i])) / (sumAdjacentGammaWeights)

	return distribution


def displayTransportTable(costMatrix,supply,demand):
	
	header = ["", " ",]
	firstRow = ['','']
	for i in range(len(supply)):
		header.append(i)
		firstRow.append(round(supply[i],3))

	t = PrettyTable(header)
	t.add_row(firstRow)
	t.add_divider()

	for i in range(len(demand)):
		row = [i, round(demand[i],3)]
		for j in range(len(costMatrix[i])):
			row.append(round(costMatrix[i][j],3))
		t.add_row(row)
		t.add_divider()
	
	print(t, "\n\n\n\n")

def Ollivier(Graph,maxIterations,normalize=True):
	
	if normalize: #normalize at t=0 before flow evolution
		totalWeight = 0
		for edge in Graph.edges:
			totalWeight += edge['weight']
		for edge in Graph.edges:
			edge['weight'] = edge['weight']/totalWeight

	for iteration in range(maxIterations):
		print('iteration -- ', iteration)
		adjMatrix = Graph.getAdjacencyMatrix()
		costMatrix = Graph.getCostMatrix(adjMatrix)

		
		for edge in Graph.edges:
			m_u = computeMassDistribution(edge['u'],adjMatrix)
			m_v = computeMassDistribution(edge['v'],adjMatrix)
			d = costMatrix[edge['u']][edge['v']]
			w = ot.emd2(m_u,m_v,costMatrix)
			try:
				edge['curvature'] = 1 - (w/d)
			except: #avoid float division by zero
				edge['curvature'] = 1 - (w/epsilon)
			#displayTransportTable(costMatrix,m_u,m_v)

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
	Graph.drawGraph(display=False)



myGraph = graphClass.CurvatureGraph(graphInput)
Ollivier(myGraph,maxIterations=2,normalize=True)