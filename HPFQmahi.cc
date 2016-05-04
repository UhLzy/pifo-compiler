/* -*-mode:c++; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */



#include <queue>
#include <cassert>

#include "queued_packet.hh"
#include "abstract_packet_queue.hh"
#include "exception.hh"

#include "priority_queue.h"
#include "calendar_queue.h"

class PIFOPacketPipeline : public AbstractPacketQueue
{
private:PriorityQueue<QueuedPacket, uint32_t> Right();
PriorityQueue<std::string, uint32_t> Root();
PriorityQueue<QueuedPacket, uint32_t> Left();
public:
    PIFOPacketPipeline( const std::string & args )
    {
        if ( not args.empty() ) {
            throw std::runtime_error( "InfinitePacketQueue does not take arguments." );
        }
    }
void enqueue( QueuedPacket && p ) override {
if(p.class==Left){Left.enq(p, getPrio(p,"Left");
Root.enq(p, getPrio(p,"Root");
}
else{Right.enq(p, getPrio(p,"Right");
Root.enq(p, getPrio(p,"Root");
}
}
uint32_t getPrio(QueuedPacket x, std::string qName) {
if(qName==Right){
static std::map<uint32_t, uint32_t> last_fin_time = {{1, 0}, {2, 0}, {3, 0}, {4, 0}, {5, 0}}; auto ret = last_fin_time.at(static_cast<uint32_t>(x("fid"))); last_fin_time.at(static_cast<uint32_t>(x("fid"))) += 1; return ret;}
else if(qName==Root){
static std::map<uint32_t, uint32_t> last_fin_time = {{1, 0}, {2, 0}, {3, 0}, {4, 0}, {5, 0}}; auto ret = last_fin_time.at(static_cast<uint32_t>(x("fid"))); last_fin_time.at(static_cast<uint32_t>(x("fid"))) += 1; return ret;}
else{
static std::map<uint32_t, uint32_t> last_fin_time = {{1, 0}, {2, 0}, {3, 0}, {4, 0}, {5, 0}}; auto ret = last_fin_time.at(static_cast<uint32_t>(x("fid"))); last_fin_time.at(static_cast<uint32_t>(x("fid"))) += 1; return ret;}
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
};