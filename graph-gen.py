from graphviz import Digraph

dot = Digraph()


strict_wfq='static std::map<uint32_t, uint32_t> last_fin_time = {{1, 0}, {2, 0}, {3, 0}, {4, 0}, {5, 0}}; auto ret = last_fin_time.at(static_cast<uint32_t>(x("class"))); last_fin_time.at(static_cast<uint32_t>(x("class"))) += 1; return ret;'

stopandgo='uint32_t now = (uint32_t) x("time");\n'
stopandgo+='static uint32_t frame_end_time=1;\nstatic uint32_t frame_begin_time;'
stopandgo+='if (now > frame_end_time){\nframe_begin_time= frame_end_time;\nframe_end_time= frame_begin_time+1;\n}\n'
stopandgo+= 'return frame_end_time;\n'


txn = header= open("tbfRight.txt",'r')
tbfRight= txn.read()


lstf="return (uint32_t) x(\"slack\");"

dot.node('Root', "Root", predicate="True", schedule=strict_wfq, shaping="NULL" )
dot.node("Left", "Left", predicate="p.class==Left", schedule=strict_wfq, shaping="NULL")
dot.node("Right", "Right", predicate = "p.class==Right", schedule=strict_wfq, shaping=tbfRight)
dot.edges([("Root","Left"),("Root","Right")])

print dot.source

dot.render('TBF.gv',view=True)
dot.save('TBF.dot')