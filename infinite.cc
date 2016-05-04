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
private:
    std::queue<QueuedPacket> internal_queue_ {};

public:
    PIFOPacketPipeline( const std::string & args )
    {
        if ( not args.empty() ) {
            throw std::runtime_error( "InfinitePacketQueue does not take arguments." );
        }
    }

    void enqueue( QueuedPacket && p ) override
    {
        internal_queue_.emplace( std::move( p ) );
    }

    QueuedPacket dequeue( void ) override
    {
        assert( not internal_queue_.empty() );

        QueuedPacket ret = std::move( internal_queue_.front() );
        internal_queue_.pop();
        return ret;
    }

    bool empty( void ) const override
    {
        return internal_queue_.empty();
    }

    std::string to_string( void ) const override
    {
        return "infinite";
    }
};

