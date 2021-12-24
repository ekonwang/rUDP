import random

from tests.BasicTest import BasicTest


class SackOutOfOrderTest(BasicTest):
    def __init__(self, forwarder, input_file):
        super(SackOutOfOrderTest, self).__init__(forwarder, input_file, sackMode = True)
        self.tick_times = 0                              # tick_times records the number of ticks
        self.temp_out_queue = []                         # temp_out_queue records the packets that are sent from sender
        
    def handle_tick(self, tick_interval):
        self.tick_times += 1
        if self.tick_times % 50 != 0:
            self.temp_out_queue.extend(filter(lambda x: x.msg_type != 'sack', self.forwarder.out_queue))
            self.forwarder.out_queue = filter(lambda x: x.msg_type == 'sack', self.forwarder.out_queue)
        else:
            self.temp_out_queue = list(set(self.temp_out_queue))
            self.forwarder.out_queue = self.temp_out_queue
            random.shuffle(self.forwarder.out_queue)
            self.temp_out_queue = []