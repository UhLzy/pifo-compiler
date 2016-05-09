from graphviz import Digraph

dot = Digraph()


strict_wfq='static std::map<uint32_t, uint32_t> last_fin_time = {{1, 0}, {2, 0}, {3, 0}, {4, 0}, {5, 0}}; auto ret = last_fin_time.at(static_cast<uint32_t>(x("class"))); last_fin_time.at(static_cast<uint32_t>(x("class"))) += 1; return ret;'

stopandgo='uint32_t now = (uint32_t) x("time");\n'
stopandgo+='static uint32_t frame_end_time=1;\nstatic uint32_t frame_begin_time;'
stopandgo+='if (now > frame_end_time){\nframe_begin_time= frame_end_time;\nframe_end_time= frame_begin_time+1;\n}\n'
stopandgo+= 'return frame_end_time;\n'


txn = header= open("tbfRight.txt",'r')
tbfRight= txn.read()

strict_wfq='static std::map<uint32_t, uint32_t> last_fin_time = {{1, 0}, {2, 0}, {3, 0}, {4, 0}, {5, 0}}; auto ret = last_fin_time.at(static_cast<uint32_t>(x("arrival_time")%2)); last_fin_time.at(static_cast<uint32_t>(x("arrival_time")%2)) += 1; return ret;'



lstf="return (uint32_t) x(\"slack\");"

dot.node('Root', "Name: Root\nPredicate: True \nSchedule: WFQ_Root \nShaping: NULL", predicate="True", schedule=strict_wfq, shaping="NULL" )
dot.node("Left", "Name: Left\nPredicate: True \nSchedule: WFQ_Left \nShaping: NULL", predicate="p.arrival_time==Left", schedule=strict_wfq, shaping="NULL")
dot.node("Right", "Name: Right \nPredicate: True \nSchedule: WFQ_Right \nShaping: TBF_RIGHT", predicate = "p.arrival_time==Right", schedule=strict_wfq, shaping="NULL")
dot.edges([("Root","Left"),("Root","Right")])

print dot.source

dot.render('TBFPaper.gv',view=True)
dot.save('TBFPaper.dot')