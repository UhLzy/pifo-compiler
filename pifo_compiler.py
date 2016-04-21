import graphviz
import pydot
import sys

##Requirements:
# pyparsing 1.5.7 (pyparsing >2.0 currently has bugs) (pip: pip install -Iv https://pypi.python.org/packages/source/p/pyparsing/pyparsing-1.5.7.tar.gz)
# pydot: https://pypi.python.org/pypi/graphviz (pip: pip install pydot)
# graphviz: https://pypi.python.org/pypi/graphviz( pip: pip install graphviz)


pifos={}
nodes=[]
nodeDict={}
edges=[]

enqueueNodes=[]

leaves=[]
dequeues=[]
enqueues=[]

class Node:
    ##simplified representation of nodes
    
    def __init__(self, gvnode):
        self.name=gvnode.obj_dict['attributes']['label']
        self.gvName=gvnode.obj_dict['name']
        self.sched=gvnode.obj_dict['attributes']['schedule']
        self.pred=gvnode.obj_dict['attributes']['predicate']
        shape="NULL"
        if "shaping" in gvnode.obj_dict['attributes'].keys():
            shape= gvnode.obj_dict['attributes']['shaping']
        self.shaping=shape
        
    def __str__(self):
        return self.name
        
class Edge:
    ##simplified representation of edges
    
    def __init__(self, gvedge):
        self.source=gvedge.obj_dict['points'][0]
        self.dest=gvedge.obj_dict['points'][1]
        
    def __str__(self):
        return str(self.source) +","+ str(self.dest)
        
def getChildren(node):
    ##Returns Nodes that are children of Node node
    name= node.gvName
    result=[]
    for edge in edges:
        if edge.source==node.gvName:
            result.append(nodeDict[edge.dest])
    return result
    
def getParent(node):
    ##Returns a Node, the parent of Node node in the tree 
    name= node.gvName
    result=None
    for edge in edges:
        if edge.dest==node.gvName:
            result=nodeDict[edge.source]
    return result

def DFS (node, level):
    ##Depth First Search Exploration that builds out the PIFO mesh (also builds out list of dequeue edges)
    if level not in pifos.keys():
        pifos[level]=[]
    pifos[level].append(node.name)
    node.level=level
    
    if node.shaping != 'NULL':
        if str(level)+"S" not in pifos.keys():
            pifos[str(level)+"S"]=[]
        pifos[str(level)+"S"].append(node.shaping)
    kids = getChildren(node)
    if len(kids)==0:
        leaves.append(node)
    else:
        dequeues.append((level, level+1))
    for kid in kids:
        DFS(kid, level+1)
        dequeues.append((node.name,kid.name))
        
def enqueue(source, node):
    ##recursively determines enqueue edges for the path of nodes from leaf to root
    enqueues.append((source, node.name))
    if node.shaping != "NULL":
        enqueues.append((source, node.shaping))
        enqueue(node.shaping, getParent(node))
    else:
        if getParent(node)!= None:
            enqueue(source, getParent(node))
            
def findRoot():
    ##Finds Root node of graph, the only node that is not a dest in any edge
    candidates= list(nodes)
    for edge in edges:
        candidates.remove(nodeDict[edge.dest])
    return candidates[0]



## Begin main function

## Input:
## Command Line input the dot file of the tree to be processed
## Ex: python pifo_compiler.py HPFQ.dot

##Returns:
## Saves a .dot file of the enqueues to xEnqueues.dot where x is the input file name
## Prints out the allocation of pifos to pifo blocks (pifos identified by label attribute)
## Displays a pdf version of the enqueues


g= pydot.graph_from_dot_file(sys.argv[1])

fileName= sys.argv[1].split('.')[0]

##Convert graph input to lists of Nodes and Edges
for node in g.get_node_list():
    temp = Node(node)
    nodes.append(temp)
    enqueueNodes.append(temp.name)
    nodeDict[temp.gvName]=temp
    
for edge in g.get_edge_list():
    edges.append(Edge(edge))
    
##DFS to build out PIFO mesh and identify leaves
DFS(findRoot(),1)

##Call enqueue on each leaf to build out enqueue edges 
for leaf in leaves:
    enqueue("EXT" + leaf.name, leaf)
    enqueueNodes.append("EXT"+leaf.name)
    
##pifos is the allocation of pifos to pifo blocks
print pifos

#Create and render the enqueue graph (dequeue edges are same as original tree structure and can be added in)
dig = graphviz.Digraph()
for node in enqueueNodes:
    dig.node(node)
dig.edges(enqueues)
dig.render(fileName+'Enqueues.gv',view=True)
dig.save(fileName+'Enqueues.dot')



    


