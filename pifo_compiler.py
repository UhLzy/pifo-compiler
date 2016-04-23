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
        self.schedule=gvnode.obj_dict['attributes']['schedule']
        self.schedule= self.schedule.replace('"','').replace("'",'"') #fix for parsing errors caused by escaped quotes
        self.predicate=gvnode.obj_dict['attributes']['predicate']
        self.predicate= self.predicate.replace('"','').replace("'",'"')
        shape="NULL"
        if "shaping" in gvnode.obj_dict['attributes'].keys():
            shape= gvnode.obj_dict['attributes']['shaping']
            shape=shape.replace('"','').replace("'",'"')
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
    pifos[level].append(node.gvName)
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
fd = file(sys.argv[1], 'rb')
data = fd.read()
fd.close()



##Processing to work around escaped quotation mark issues, second stage of fix in node constructor
x= data.replace('\\"', "'")

g= pydot.graph_from_dot_data(x)

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
dig.render(fileName+'Enqueues.gv',view=False)
dig.save(fileName+'Enqueues.dot')


##Output string for pifo-machine

pipeline = 'PIFOPipeline ' + fileName+ '_pipeline({'
stageBase = 'PIFOPipelineStage('
for block in pifos.keys():
    numQueues=len(pifos[block])
    lookup_table= '{'
    packet_field='fid'
    schedule='[] (const auto & x) {'
    if type(block) == str:
        ##shaping
        for node in nodes:
            if node.level==int(block[:1]) and node.shaping !="NULL":
                lookup_table+= '{'+node.predicate+', {Operation::ENQ,' + getParent(node).gvName + '}},'
                schedule += node.shaping
    else:
        for node in nodes:
            if node.level==block:
                predicate=node.predicate
                if node in leaves:
                    lookup_table+= '{'+node.predicate+', {Operation::TRANSMIT, {}}},'
                else:
                    kids=getChildren(node)
                    for kid in kids:
                        lookup_table+= '{'+kid.predicate+', {Operation::DEQ,' + kid.gvName+ '}},'
                schedule+=node.schedule
    lookup_table+='},'
    schedule+='})'
    blockString= stageBase+str(numQueues)+ ','+packet_field+',' + lookup_table + schedule
    pipeline+=blockString+','
    
    
#numQueues=1
#packet_field="fid"
#lookup_table= '{{1, {Operation::TRANSMIT, {}}}, {2, {Operation::TRANSMIT, {}}},},'
#schedule = '[] (const auto & x) { return x("fid"); })'

pipeline+='});'

print pipeline


    


