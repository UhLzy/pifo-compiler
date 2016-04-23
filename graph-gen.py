from graphviz import Digraph

dot = Digraph()


dot.node('Root', "Root", predicate="True", schedule="WFQ_Root", shaping="NULL" )
#dot.node("Left", "Left", predicate="p.class==Left", schedule="WFQ_Left", shaping="NULL")
#dot.node("Right", "Right", predicate = "p.class==Right", schedule="WFQ_Right", shaping="TBF_Right")
#dot.edges([("Root","Left"),("Root","Right")])

print dot.source

dot.render('TBF.gv',view=True)
dot.save('TBF.dot')