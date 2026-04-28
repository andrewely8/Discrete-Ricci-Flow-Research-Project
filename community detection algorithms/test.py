import os
import numpy as np
import graphClass
import graphNetworks
import networkx as nx
import ot
import sys
from prettytable import PrettyTable

# complete 3-graph
#graphInput = [(0, 1, 1), (0, 2, 1), (1, 2, 1),]

# complete 3-graph with 1 more edge
#graphInput = [(0, 1, 1), (0, 2, 1), (1, 2, 1), (2, 3, 1),]

# complete 4-graph
#graphInput = [(0, 1, 1), (0, 2, 1), (0, 3, 1), (1, 2, 1), (2, 3, 1),(1, 3, 1),]

# complete 4-graph with 1 more edge
#graphInput = [(0, 1, 1), (0, 2, 1), (0, 3, 1), (1, 2, 1), (2, 3, 1),(1, 3, 1),(3,4,1)]

# complete 5-graph
#graphInput = [(0, 1, 1), (0, 2, 1), (0, 3, 1), (0, 4, 1), (1, 2, 1), (1, 3, 1), (1, 4, 1), (2, 3, 1), (2, 4, 1), (3, 4, 1)]

# complete 5-graph with 1 more edge
#graphInput = [(0, 1, 1), (0, 2, 1), (0, 3, 1), (0, 4, 1), (1, 2, 1), (1, 3, 1), (1, 4, 1), (2, 3, 1), (2, 4, 1), (3, 4, 1), (4,5,1)]

# complete 6-graph
#graphInput = [(0,1,1), (0,2,1), (0,3,1), (0,4,1), (0,5,1), (1,2,1), (1,3,1), (1,4,1), (1,5,1), (2,3,1), (2,4,1), (2,5,1), (3,4,1), (3,5,1), (4,5,1),]

# complete 6-graph with 1 more edge
#graphInput = [(0,1,1), (0,2,1), (0,3,1), (0,4,1), (0,5,1), (1,2,1), (1,3,1), (1,4,1), (1,5,1), (2,3,1), (2,4,1), (2,5,1), (3,4,1), (3,5,1), (4,5,1), (5,6,1),]

#Two complete 3 graphs connected by 1 edge.
#graphInput = [(0,1,1),(0,2,1),(2,1,1),(2,3,1),(3,4,1),(3,5,1),(4,5,1),]


#complete 3 graph with more edge, with an extended path.
#graphInput = [(0, 1, 1), (0, 2, 1), (1, 2, 1), (2, 3, 1),(3,4,1),(4,5,1),]

#complete 3 graph with one more edge from each node. 
#graphInput = [(0, 1, 1), (0, 2, 1), (1, 2, 1),(0,3,1),(1,4,1),(2,5,1)]



#'caterpillar trees' with center nodes as complete 3 graphs.
# graphInput = [(0,1,1),(0,2,1),(1,2,1),(1,3,1),(2,4,1),(4,5,1),
# 			  (4,6,1),(5,6,1),(5,7,1),(6,8,1),(8,10,1),(8,9,1),
# 			  (9,10,1),(10,11,1),(10,12,1),(10,13,1),(10,14,1),
# 			  (9,15,1),(15,17,1),(15,16,1),(16,17,1),(16,18,1),
# 			  (18,20,1),(18,19,1),(19,20,1),(20,21,1),]

graphInput = [(0,1,1),(0,2,1),(1,2,1),(1,3,1),(2,4,1),(4,5,1),(5,6,1),(4,6,1),
			  (5,7,1),(5,8,1),(5,9,1)]



epsilon = 10**(-5)
dt = 0.001 #derivative step rate
alpha = 0.99 #for LLY curavture limit as alpha -> 1

# gamma(x) = x  for now.
def gamma(x):
	return 1/x

def computeMassDistribution(vertex,adjMatrix,alpha=0.2):
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


def displayTransportTable(costMatrix,supply,demand,optimalCost,optimalPlan):
	
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
	
	print(t)
	print("optimal transportation plan: \n", optimalPlan['G'].T)
	print("optimal transportation cost: ", optimalCost)
	print("\n\n\n\n")


def deleteZeroWeightEdges(Graph):
	for edge in Graph.edges[:]: #iterate over a copy of the list
		if edge['weight'] <= epsilon:
			Graph.removeEdge(edge)
			print('removed edge: ', edge)


def checkDistances(Graph,costMatrix,violation):
	for edge in Graph.edges:
		if costMatrix[edge['u']][edge['v']] != edge['weight']:
			print(f'\tshortest path between {edge['u']} and {edge['v']} is not edge weight ({edge['u']},{edge['v']})')
			violation = True
	print('')
	return(violation)

def Ollivier(Graph,maxIterations,normalize=True,removeZeroWeight=True,displayTransportTables=True):
	
	violation = False #used to check if at any iteration we w(u,v) != d(u,v).
	Graph.drawGraph(display=True)

	if normalize: #normalize at t=0 before flow evolution
		totalWeight = 0
		for edge in Graph.edges:
			totalWeight += edge['weight']
		for edge in Graph.edges:
			edge['weight'] = edge['weight']/totalWeight

	for iteration in range(maxIterations):
		print('iteration -- ', iteration)

		#remove 0 weight edges
		if removeZeroWeight:
			deleteZeroWeightEdges(Graph)
			print('')

		adjMatrix = Graph.getAdjacencyMatrix()
		costMatrix = Graph.getCostMatrix(adjMatrix)

		violation = checkDistances(Graph,costMatrix,violation)

		for edge in Graph.edges:


			m_u = computeMassDistribution(edge['u'],adjMatrix)
			m_v = computeMassDistribution(edge['v'],adjMatrix)
			d = costMatrix[edge['u']][edge['v']]
			if displayTransportTables and edge['u']==1 and edge['v']==2: #ONLY LOOKING AT ONE EDGE FOR NOW
				emd = ot.emd2(m_u,m_v,costMatrix,return_matrix=True)
				w = emd[0]
				plan = emd[1]
				print(f'EDGE ({edge['u']}, {edge['v']})')
				displayTransportTable(costMatrix,m_u,m_v,w,plan)
			else:
				w =  ot.emd2(m_u,m_v,costMatrix)
			try:
				k_alpha = 1 - (w/d)
				edge['curvature'] = k_alpha / (1-alpha)
			except: #avoid float division by zero
				k_alpha = 1 - (w/epsilon)
				edge['curvature'] = k_alpha / (1-alpha)
				

		if normalize:
			norm = 0
			for edge in Graph.edges:
				norm += edge['weight']*edge['curvature']
			for edge in Graph.edges:
				edge['weight'] = edge['weight'] + dt * (-1*edge['curvature']*edge['weight'] + edge['weight']*norm)

		elif not normalize:
			for edge in Graph.edges:
				edge['weight'] = edge['weight'] + dt * (-1*edge['curvature']*edge['weight'])


	print('\n-- Finished Ricci Flow -- ')
	if violation:
		print(f'distance vs edge weight: d(u,v) does not equal w(u,v) for some time')
	else:
		print(f'distance vs edge weight: d(u,v) = w(u,v) for all time')


	#Display results and end graph
	print('Final edge weights and curvatures: \n')
	for edge in Graph.edges:
		print(edge)
	Graph.drawGraph(display=True)



myGraph = graphClass.CurvatureGraph(graphInput)
Ollivier(myGraph,maxIterations=1000,normalize=True,removeZeroWeight=True,displayTransportTables=True)