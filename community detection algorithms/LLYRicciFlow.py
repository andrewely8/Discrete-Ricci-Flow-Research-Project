import os
import numpy as np
import graphClass
import graphNetworks
import testGraphs
import networkx as nx
import ot
import sys
import matplotlib.pyplot as plt
from prettytable import PrettyTable

epsilon = 10**(-5)
deleteThreshold = 0.05
dt = 0.25 #derivative step rate
alpha = 0.99 #for LLY curavture limit as alpha -> 1

# gamma(x) = 1/x.
def gamma(x):
	return 1/x

def computeMassDistribution(vertex,adjMatrix,alpha=alpha):
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


def drawWeightsGraph(title, savePath=None ):
    edge_series = {}
    curvature_series = {}
    offset_amount=0.005

    # First collect data normally
    for track in storedWeights:
        t = track["time"]

        for edge in track["edges"]:
            label = f"({edge['u']}, {edge['v']})"

            if label not in edge_series:
                edge_series[label] = {"x": [], "y": []}

            if label not in curvature_series:
                curvature_series[label] = {"x": [], "y": []}

            edge_series[label]["x"].append(t)
            edge_series[label]["y"].append(edge["weight"])

            curvature_series[label]["x"].append(t)
            curvature_series[label]["y"].append(edge["curvature"])

    # Assign a fixed offset to each edge
    labels = list(edge_series.keys())
    edge_offsets = {
        label: i * offset_amount
        for i, label in enumerate(labels)
    }

    # Plot edge weights
    plt.figure()

    for label, data in edge_series.items():
        offset = edge_offsets[label]
        shifted_y = [y + offset for y in data["y"]]

        plt.plot(data["x"],shifted_y,label=f"{label}")

    plt.xlabel("time")
    plt.ylabel("edge weight")
    plt.title(f"{title} Ricci Flow Edge Weights")
    plt.legend()

    if savePath:
        plt.savefig(savePath+f"{title}_edgeWeights.png")
        plt.close()
    else:
        plt.show()

    # Assign a fixed offset to each curvature
    labels = list(curvature_series.keys())
    curvature_offsets = {
        label: i * offset_amount
        for i, label in enumerate(labels)
    }

    # Plot edge curvatures
    plt.figure()

    for label, data in curvature_series.items():
        offset = curvature_offsets[label]
        shifted_y = [y + offset for y in data["y"]]

        plt.plot(data["x"],shifted_y,label=f"{label}")

    plt.xlabel("time")
    plt.ylabel("edge curvature")
    plt.title(f"{title} Ricci Flow Edge Curvature")
    plt.legend()

    if savePath:
        plt.savefig(savePath+f"{title}_edgeCurvatures.png")
        plt.close()
    else:
        plt.show()


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
		if edge['weight'] <= deleteThreshold:
			Graph.removeEdge(edge)
			print('removed edge: ', edge)


def checkDistances(Graph,costMatrix,violation):
	for edge in Graph.edges:
		if costMatrix[edge['u']][edge['v']] != edge['weight']:
			print(f'\tshortest path between {edge['u']} and {edge['v']} is not edge weight ({edge['u']},{edge['v']})')
			violation = True
	return(violation)

def Ollivier(Graph,maxIterations,normalize=True,removeZeroWeight=True,displayTransportTables=True,trackWeights=True,savePath=None):
	
	violation = False #used to check if at any iteration we w(u,v) != d(u,v).
	if savePath:
		initialPath = savePath+"_initial.png"
		Graph.drawGraph(display=True,savePath=initialPath)
	else:
		Graph.drawGraph(display=True)

	if normalize: #normalize at t=0 before flow evolution
		totalWeight = 0
		for edge in Graph.edges:
			totalWeight += edge['weight']
		for edge in Graph.edges:
			edge['weight'] = edge['weight']/totalWeight

	for iteration in range(maxIterations):
		#print('iteration -- ', iteration)

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
				

		#store current edge weights and curvatures (before updating edge weight)
		if trackWeights:
			m = {"time": iteration,"edges": [{"u": edge["u"],"v": edge["v"],"weight": edge["weight"], "curvature": edge["curvature"]} for edge in Graph.edges]}
			storedWeights.append(m)

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
		print(f'distance vs edge weight: d(u,v) does not equal w(u,v) for some time -- distance condition violated')
	else:
		print(f'distance vs edge weight: d(u,v) = w(u,v) for all time')

	#remove 0 weight edges
	if removeZeroWeight:
		deleteZeroWeightEdges(Graph)

	#Display results and end graph
	print('Final edge weights and curvatures: \n')
	for edge in Graph.edges:
		print(edge)
	prefix = "Unnormalized"
	if normalize:
		prefix="Normalized"
	if savePath:
		finishedPath = savePath + f"_{prefix}_limitting.png"
		Graph.drawGraph(display=True,savePath=finishedPath)
	else:
		Graph.drawGraph(display=True)
	if trackWeights:
		drawWeightsGraph(prefix,savePath=savePath)



#Adjust initially equal edge weights slightly so final visual plots do not have a lot of overlap.
# for g in testGraphs.graphs:
# 	numEdges = len(testGraphs.graphs[g])
# 	spacingFactor = 0.1
# 	spacing = 1/numEdges * spacingFactor
# 	start = 1 - spacing * numEdges
# 	for i in range(numEdges):
# 		u = testGraphs.graphs[g][i][0]
# 		v = testGraphs.graphs[g][i][1]
# 		w = start + spacing * i
# 		t = (u,v,w)
# 		testGraphs.graphs[g][i] = t

#Run on all graphs in testGraphs.py
# for g in testGraphs.graphs:
# 	storedWeights = []
# 	grph = graphClass.CurvatureGraph(testGraphs.graphs[g])
# 	os.makedirs(f"graphOutputs/{g}",exist_ok=True)
# 	savePath = f"graphOutputs/{g}/{g}_"
# 	Ollivier(grph,maxIterations=100,normalize=True,removeZeroWeight=True,displayTransportTables=False, trackWeights=True,savePath=savePath)
# 	storedWeights = []
# 	grph = graphClass.CurvatureGraph(testGraphs.graphs[g])
# 	Ollivier(grph,maxIterations=100,normalize=False,removeZeroWeight=True,displayTransportTables=False, trackWeights=True,savePath=savePath)



#Manual run on one graph
myGraph = graphClass.CurvatureGraph(testGraphs.graphs["G1"])
storedWeights = []
savePath = None #f"graphOutputs/G1/G1_"
Ollivier(myGraph,maxIterations=100,normalize=True,removeZeroWeight=True,displayTransportTables=False, trackWeights=True,savePath= savePath)
