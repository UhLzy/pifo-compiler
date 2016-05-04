PriorityQueue<QueuedPacket, uint32_t> Right();
PriorityQueue<std::string, uint32_t> Root();
PriorityQueue<QueuedPacket, uint32_t> Left();
void enqueue( QueuedPacket && p ) override {
if(p.class==Left){Left.enq(p, getPrio(p,"Left");
Root.enq(p, getPrio(p,"Root");
}
else{Right.enq(p, getPrio(p,"Right");
Root.enq(p, getPrio(p,"Root");
}
}
QueuedPacket dequeue( void ) override {
std::string refRoot = Root.dequeue();
if ("Left"== refRoot){
return Left.dequeue();
}
else{
return Right.dequeue();
}
}
