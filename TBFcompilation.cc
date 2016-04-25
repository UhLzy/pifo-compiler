#include <iostream>
#include <random>

#include "pifo_pipeline_stage.h"
#include "pifo_pipeline.h"

int main() {
  try {
    // Random number generation
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<int> ele_dis(1, 2);

    // Traffic generation
    PIFOPacket test_packet;

    // Single PIFO pipeline stage consisting of
    // 1 priority and queue
    // (every PIFO pipeline stage has 1 calendar queue)
PIFOPipelineStage pifo1(1,
class,
{{Left, {Operation::DEQ, pifo2}},{Right, {Operation::DEQ, pifo2}},},
[] (const auto & x) {if (x("ptr")==666){WFQ_Root}
});
PIFOPipelineStage pifo2(2,
class,
{{Right, {Operation::TRANSMIT, {}}},{Left, {Operation::TRANSMIT, {}}},},
[] (const auto & x) {if (x("class")==Right){WFQ_Right}
if (x("class")==Left){WFQ_Left}
});
PIFOPipelineStage pifo2S(1,
class,
{{Right, {Operation::ENQ,Root}},},
[] (const auto & x) {if (x("class")==Right){TBF_Right}});
PIFOPipeline TBF_pipeline({pifo1,pifo2,pifo2S,});
PIFOPipeline mesh=TBF_pipeline;
for (uint32_t i = 0; i < 10000; i++) {
      if(ele_dis(gen)==1){test_packet("class") = "Left";}
      else{test_packet("class") = "Right";}
      
      test_packet("ptr") = 666;
      mesh.enq(0, QueueType::PRIORITY_QUEUE, 0, test_packet, i);
    }

    std::cout << "Finished enqs\n";

    for (uint32_t i = 10000; i < 20000; i++) {
      auto result = mesh.deq(0, QueueType::PRIORITY_QUEUE, 0, i);
      std::cout << "Deq result is \"" << result << "\"" << std::endl;
    }

    assert_exception(mesh.deq(0, QueueType::PRIORITY_QUEUE, 0, 20000).initialized() == false);
  } catch (const std::exception & e) {
    std::cerr << "Caught exception in main " << std::endl << e.what() << std::endl;
    return EXIT_FAILURE;
  }
}