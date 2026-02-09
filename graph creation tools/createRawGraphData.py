
inputFile = 'email-Eu-core/email-Eu-core.txt'
outputFile = 'outputGraph.txt'

graph = []

with open(inputFile, "r") as file:
	for line in file:
		line = line.strip()
		line = line.split(' ')
		try:
			graph.append((int(line[0]),int(line[1]),1)) #-1 might be needed to convert from 1 indexed to 0 indexed.
		except:
			print('could not process line: ', line)

with open(outputFile, 'w') as file:
	file.write('euEmailCore = [ \n\t')
	i = 1
	for edge in graph:
		file.write(f'{edge},\t')
		if i == 10:
			file.write('\n\t')
			i = 0
		i+=1 
	file.write('\n]')
	

print(graph)