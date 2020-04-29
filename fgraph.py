import gdb
import networkx as nx
from networkx.drawing.nx_agraph import write_dot

def addEdge(graph, edgeFrom, edgeTo):
	if edgeFrom in graph and edgeTo in graph and not graph.has_edge(edgeFrom, edgeTo):
		graph.add_edge(edgeFrom, edgeTo)	

def removeSym(name):
	if "@" in name:
		return name[:name.index("@")]
	if "+" in name:
		return name[:name.index("+")]
	return name


def parseWhere(where):
	stk = []
	lines = where.splitlines()
	for line in lines:
		words = line.split()
		if len(words) > 2 and words[2] == "in":
			stk.append(removeSym(words[3]))
		else:
			stk.append(removeSym(words[1]))
	return stk


def runOption(binaryIndex, graph):
	runStr = "run"
	if "a" in argv[0]:
		for i in range(binaryIndex + 1, len(argv), 1):
			runStr = runStr + " " + argv[i]
	if "i" in argv[0]:
		runStr = runStr + " < " + argv[binaryIndex - 1]
	
	try:
		gdb.execute(runStr, False, True)
	except gdb.error:
		print("Input file not found.")
		return

	prevStk = None	
	while True:
		try:
			where = gdb.execute("where", False, True)
		except gdb.error:
			break;
		currStk = parseWhere(where)

		if len(currStk) > 1:
			for i in range(1, len(currStk), 1):
				if currStk[i] in graph:
					addEdge(graph, currStk[i], currStk[0])
					break
		elif len(currStk) == 1 and prevStk is not None:
			for i in range(len(prevStk) - 1, -1, -1):
				if prevStk[i] in graph:
					addEdge(graph, prevStk[i], currStk[0])
					break
		
		prevStk = currStk
		gdb.execute("continue", False, True)

def possibleOption(binaryIndex, graph):
	instructions = ["call", "jmp", "je", "jne", "jg", "jge", "ja", "jae", "jl", "jle", "jb", "jbe", "jo", "jno", "jz", "jnz", "js", "jns", "jcxz", "jecxz", "jrcxz"]
	for node in graph:
		try:
			disas = gdb.execute("disassemble " + node, False, True)
		except gdb.error:
			continue
		lines = disas.splitlines()
		for line in lines:
			words = line.split()
			if len(words) > 2 and words[2] in instructions:
				function = words[len(words) - 1]
				if function.startswith("<") and function.endswith(">"):
					toFunction = removeSym(function[1:len(function) - 1])
					if toFunction == node and words[2] == "call":
						addEdge(graph, node, node)
					elif toFunction != node:
						addEdge(graph, node, toFunction)

def setUpNodes():
	graph = nx.DiGraph()
	nodes = gdb.execute("rbreak", False, True)
	
	for lines in nodes.splitlines():
		words = lines.split()
		if words[0] != "Breakpoint":
			node = words[len(words) - 1]
			node = node[:len(node) - 1]
			graph.add_node(removeSym(node))

	breakpts = gdb.breakpoints()
	for breakpt in breakpts:
		breakpt.silent = True
	return graph

def writeGraph(graph):
	if "r" in argv[0]:
		graph.remove_nodes_from(list(nx.isolates(graph)))
	if "s" in argv[0]:
		write_dot(graph, argv[1] + ".dot")
	else:
		write_dot(graph, "fgraphout.dot")

def main():
	binaryIndex = 1
	if "s" in argv[0]:
		binaryIndex = binaryIndex + 1
	if "i" in argv[0]:
		binaryIndex = binaryIndex + 1

	try:	
		gdb.execute("file " + argv[binaryIndex])
	except gdb.error:
		print("Binary file not found or not in an executable format.")
		gdb.execute("quit")

	gdb.execute("set disassembly-flavor intel", False, True)

	print("Creating nodes.")	
	graph = setUpNodes()

	print("Creating edges.")
	if "p" in argv[0]:
		possibleOption(binaryIndex, graph)
	elif "r" in argv[0]:
		runOption(binaryIndex, graph)

	print("Generating graph.")
	writeGraph(graph)
	gdb.execute("quit")

if __name__ == "__main__":
	main()
