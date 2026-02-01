#Ricci Curvature for trees which follows a simplified algorithm due to the non-cyclic structure of trees.

#Binary Tree
# V = 15
# E = [[0,1,1],[0,2,1],[1,3,1],[1,4,1],[2,5,1],[2,6,1],[3,7,1],
# 	 [3,8,1],[4,9,1],[4,10,1],[5,11,1],[5,12,1],[6,13,1],[6,14,1]]

#Caterpillar Tree
V = 15
E = [[0,4,1],[0,5,1],[0,1,1],[1,6,1],[1,7,1],[1,8,1],[1,2,1],
	 [2,9,1],[2,3,1],[3,10,1],[3,11,1],[3,12,1],[3,13,1],]

#Level 2 star graph
# V = 11
# E = [[0,1,3],[0,2,1],[0,3,0.5],[0,4,3],[0,5,4],[1,6,5],[2,7,1],[3,8,6],[4,9,2],[5,10,8]]

#path graph length 4
# V = 5
# E = [[0,1,1],[1,2,1],[2,3,1],[3,4,1]]


def computeDegrees(edgeSet, numVerticies):
	degrees = [0 for _ in range(numVerticies)]
	
	for edge in edgeSet:
		u = edge[0]
		v = edge[1]
		degrees[u] += 1
		degrees[v] += 1
	return degrees


def computeD(vertex,edgeSet):
	D = 0
	for edge in edgeSet:
		if edge[0] == vertex or edge[1] == vertex:
			D += 1/edge[2]
	return D


#mode = 'values' := we are passing a tree with numerical edge weights like 0,2,5,3 etc.
#mode = 'equations' := we are passing a tree with variable edge weights like w_{11},w{ab},w{uv}, etc.
def computeCurvatures(edgeSet,degrees,mode):
	if mode == 'values':
		curvatures = [0 for _ in range(len(edgeSet))]
		for i,edge in enumerate(edgeSet):
			u = edge[0]
			v = edge[1]
			weight = edge[2]
			Du = computeD(u,edgeSet)
			Dv = computeD(v,edgeSet)
			curvatures[i] = (2-degrees[u])/(weight*Du) + (2-degrees[v])/(weight*Dv)

	elif mode == 'equations':
		curvatures = ['' for _ in range(len(degrees))] #len of degrees is the number of vertices

	return curvatures


def computeNormalizedFlow(curvatures,edgeSet):
	flows = [0 for _ in range(len(edgeSet))]
	normalizedSum = 0
	for i,c in enumerate(curvatures):
		normalizedSum += c*edgeSet[i][2]
	for i,edge in enumerate(edgeSet):
		flows[i] = -1*curvatures[i]*edgeSet[i][2] + edgeSet[i][2]*normalizedSum
	return flows


def computeUnnormalizedFlow(curvatures,edgeSet):
	flows = [0 for _ in range(len(edgeSet))]
	for i,edge in enumerate(edgeSet):
		flows[i] = -1*curvatures[i]*edgeSet[i][2]
	return flows


#mode = 'normalized' uses normalization of edge weights
#mode = 'unnormalized' uses unnomralized edge weights
def ricciFlowValues(edgeSet,numVerticies,iterations, mode):

	#Normalize at t=0 before flow procedure
	if mode == 'normalized':
		totalWeight = 0
		for edge in edgeSet:
			totalWeight += edge[2]
		for edge in edgeSet:
			edge[2] = edge[2] / totalWeight

	degrees = computeDegrees(edgeSet,numVerticies)

	print(f"\nt={0} Edge weights: \n")
	for edge in edgeSet:
		print(f"edge: ({edge[0]},{edge[1]}) \t weight: {edge[2]:.3f}")
	print('\n')	

	for i in range(iterations):

		#Implement divison by zero check (exit conditions, delete edges, contract edges. etc.)
		#For now, just force edge weights to be small non zero positive number.
		for edge in edgeSet:
			if edge[2] == 0:
				edge[2] = 0.000001

		curvatures = computeCurvatures(edgeSet,degrees,'values')
		if mode == 'normalized':
			flows = computeNormalizedFlow(curvatures,edgeSet)
		elif mode == 'unnormalized':
			flows = computeUnnormalizedFlow(curvatures,edgeSet)
		else:
			print("error: Invalid normalization/unnormalization mode specified")
		for j,edge in enumerate(edgeSet):
			edge[2] += flows[j] 
			

		print(f"\nt={i+1} Edge weights and curvatures: \n")
		for j,edge in enumerate(edgeSet):
			print(f"edge: ({edge[0]},{edge[1]}) \t weight: {edge[2]:.3f} \t curvature: {curvatures[j]:.3f}")
		print('\n')	


def ricciFlowEquations(edgeSet,numVerticies):
	pass

ricciFlowValues(E,V, 1000, 'normalized')