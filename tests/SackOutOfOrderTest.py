import random

from tests.BasicTest import BasicTest


class SackOutOfOrderTest(BasicTest):
    def __init__(self, forwarder, input_file):
        super(SackOutOfOrderTest, self).__init__(forwarder, input_file, sackMode = True)
        self.tick_times = 0                              # tick_times records the number of ticks
        self.queue = []                         # queue records the packets that are sent from sender
        
    def handle_tick(self, tick_interval):
        self.tick_times += 1
        if self.tick_times % 50 != 0:
            self.queue.extend(filter(lambda x: x.msg_type != 'sack', self.forwarder.out_queue))
            self.forwarder.out_queue = filter(lambda x: x.msg_type == 'sack', self.forwarder.out_queue)
        else:
            self.queue = list(set(self.queue))
            self.forwarder.out_queue = self.queue
            random.shuffle(self.forwarder.out_queue)
            self.queue = []