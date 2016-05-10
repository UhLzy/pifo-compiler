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

enqMap={}
extPreds={}

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
        
        self.fieldMatch="666"
        
        self.packetField='"ptr"'
        if "." in self.predicate:
            self.packetField='"'+self.predicate.split('=')[0].split('.')[1]+'"' #maybe make more general?
            self.fieldMatch=self.predicate.split('==')[1]
            if self.fieldMatch.lower()=="left":
                self.fieldMatch="1"
            else:
                self.fieldMatch="2"
        
        
        
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
    enqMap[source].append(node)
    if node.shaping != "NULL":
        enqueues.append((source, node.name + "S"))
        enqMap[node.name+"S"]=[]
        enqueue(node.name+"S", getParent(node))
    else:
        if getParent(node)!= None:
            enqueue(source, getParent(node))
            
def findRoot():
    ##Finds Root node of graph, the only node that is not a dest in any edge
    candidates= list(nodes)
    for edge in edges:
        candidates.remove(nodeDict[edge.dest])
    return candidates[0]
    
def getPrioIndex(node):
    if node.fieldMatch=="666" or node.fieldMatch=="1":
        return "0"
    else:
        return "1"
    



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
    enqMap["EXT"+leaf.name]=[]
    extPreds["EXT"+leaf.name]="test_packet("+leaf.packetField +")=="+leaf.fieldMatch 
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
outFile=open(fileName+'compilation.cc', 'w')

header= open("machine_header.txt",'r')
for line in header:
    outFile.write(line)

pipeline = 'PIFOPipeline ' + fileName+ '_pipeline({'
stageBase = 'PIFOPipelineStage pifo'

outputBlocks=[]

#outVars = open('compilation.txt', 'w')
indices={}
i=0
for block in pifos.keys():
    print str(block)
    indices[block] = i
    i+=1
    start= stageBase+str(block) + "("
    
    numQueues=len(pifos[block])
    lookup_table= '{'
    packet_field='fid' #default for now
    schedule='[] (const auto & x) {'
    if type(block) == str:
        ##shaping
        for node in nodes:
            if node.level==int(block[:1]) and node.shaping !="NULL":
                packet_field= node.packetField
                argName= 'Starget'+node.gvName
                pifoArgs= 'std::vector<PIFOArguments> '+ argName+'={{' +str(getParent(node).level-1)+',QueueType::PRIORITY_QUEUE,' + getPrioIndex(getParent(node))+'}};\n'
                outVars.write(pifoArgs)
                outFile.write(pifoArgs)
                lookup_table+= '{'+node.fieldMatch+', {Operation::ENQ,' + argName + '}},'
                schedule += "if (x("+node.packetField +")=="+node.fieldMatch + "){"+node.shaping+"}"
    else:
        for node in nodes:
            if node.level==block:
                packet_field= node.packetField
                if node in leaves:
                    lookup_table+= '{'+node.fieldMatch+', {Operation::TRANSMIT, {}}},'
                else:
                    kids=getChildren(node)
                    for kid in kids:
                        packet_field=kid.packetField
                        argName= 'target'+kid.gvName
                        pifoArgs= 'std::vector<PIFOArguments> '+ argName+'={{' +str(kid.level-1)+',QueueType::PRIORITY_QUEUE,' + getPrioIndex(kid)+'}};\n'
                        outVars.write(pifoArgs)
                        outFile.write(pifoArgs)
                        lookup_table+= '{'+kid.fieldMatch+', {Operation::DEQ,' + argName+'}},'
                schedule += "if (x("+node.packetField +")=="+node.fieldMatch + "){"+node.schedule+"}\n"
    lookup_table+='},'
    baseCase = 'uint32_t y =0; return y;'
    schedule+=baseCase
    schedule+='})'
    blockString= start+str(numQueues)+ ',\n'+packet_field+',\n' + lookup_table +"\n"+ schedule
    outVars.write(blockString + ";\n")
    outFile.write(blockString + ";\n")
    pipeline+="pifo" + str(block)+','
    
    
#numQueues=1
#packet_field="fid"
#lookup_table= '{{1, {Operation::TRANSMIT, {}}}, {2, {Operation::TRANSMIT, {}}},},'
#schedule = '[] (const auto & x) { return x("fid"); })'

pipeline+='});\n'

outVars.write(pipeline)
outFile.write(pipeline)

##Test of writing full machine.cc

rename = 'PIFOPipeline mesh=' + fileName+ '_pipeline;\n'

outFile.write(rename)


mid= open("machine_mid.txt",'r')

for line in mid:
    outFile.write(line)
    
    
enq=""
keys= extPreds.keys()
for i in range(len(keys)):
    if i==0:
        enq+= "if("+extPreds[keys[i]] + "){"
    elif i== (len(keys)-1):
        enq+= "else{"
    else:
        enq+= "else if("+extPreds[keys[i]]+"){"
    for target in enqMap[keys[i]]:
        enq += "mesh.enq("+str(target.level-1)+",QueueType::PRIORITY_QUEUE,"+str(getPrioIndex(target))+",test_packet,i);\n"
        if target.shaping != "NULL":
            enq+= "mesh.enq(" +str(indices[str(target.level)+"S"])+",QueueType::CALENDAR_QUEUE,0, test_packet,i);\n"
    enq+="}\n"

outFile.write(enq)



footer= open("machine_footer.txt",'r')

for line in footer:
    outFile.write(line)


    


