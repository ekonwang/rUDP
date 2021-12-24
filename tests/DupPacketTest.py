import random

from tests.BasicTest import BasicTest

class DupPacketTest(BasicTest):
    def __init__(self, forwarder, input_file, lost_packets=None, lost_times=3, lost_rate=0.2):
        """initialize the test
        Args:
            forwarder ([Forwarder]): the forwarder to be tested
            input_file ([file]): read from this file
            lost_packets ([list], optional): the packets that should be lost. Defaults to None.
            lost_times ([int], optional): the times that the packets will be lost. Defaults to 3.
            lost_rate ([float], optional): if haven't indicated lost_packets, we will lost packet randomly and this param will be the lost rate. Defaults to 0.2.
        """
        super().__init__(forwarder, input_file)
        self.lost_times = lost_times
        self.lost_rate = lost_rate
        self.lost_counts = dict()
        if not lost_packets:
            self.lost_packets = []
            self.indicated = False
            self.checked_seqno = set()
        else:
            print("lost packets:", lost_packets)
            self.lost_packets = lost_packets
            self.indicated = True
            for p in self.lost_packets:
                self.lost_counts[p] = 0
        
        
    def handle_packet(self):
        if self.indicated:
            for p in self.forwarder.in_queue:
                self.handle_lost(p)
        else:
            for p in self.forwarder.in_queue:
                if p.seqno in self.checked_seqno:
                    self.handle_lost(p)
                else:
                    self.checked_seqno.add(p.seqno)
                    if random.random() < self.lost_rate:
                        print("lost packet:", p.seqno)
                        self.lost_packets.append(p.seqno)
                        self.lost_counts[p.seqno] = 0
                    self.handle_lost(p)
                        
    def handle_lost(self, packet):
        """check if the packet shoule be lost and handle it accordingly
        Args:
            packet ([Packet]): the packet to be checked
        """
        if packet.seqno in self.lost_packets and packet.msg_type == 'data':
            self.lost_counts[packet.seqno] += 1
            if self.lost_counts[packet.seqno] > self.lost_times:
                print('Enough lost times, send the packet:',packet)
                self.forwarder.out_queue.append(packet)
                self.lost_counts[packet.seqno] = 0
        else:
            self.forwarder.out_queue.append(packet)
        
            

        # empty out the in_queue
        self.forwarder.in_queue = []