import sys
import getopt
import time
import random

import Checksum
import BasicSender

'''
This is a skeleton sender class. Create a fantastic transport protocol here.
'''
class Sender(BasicSender.BasicSender):
    def __init__(self, dest, port, filename, debug=False, sackMode=False):
        super(Sender, self).__init__(dest, port, filename, debug)
        self.randstart = 0
        self.timeout = 0.5
        self.sack = sackMode
        self.MAX_WDN = 5        # send window size.
        self.window = []        # store list of [package, ack_times, last_sent_timestamp].
        if sackMode:
            self.threshould = 3     # if ack_times > threshould, execute resend.

    # Main sending loop.
    def start(self):
        if self.randstart == None:
            self.randstart = random.randint(233, 23333)
        self.expected_ack = self.randstart
        self.ifend = False
        while self.ifend == False or len(self.window) > 0: # while data have not all be transfered.    
            self.send_all()
            wait_time = self.get_wait_time()
            recv = self.receive(wait_time)
            if recv == None:
                self.handle_timeout()
            else:
                recv = recv.decode()
                self.handle_resp(recv)

    def get_wait_time(self):
        res = self.window[0][2] + float(self.timeout)
        res = max((res - time.time()), 0.)

        return res

    def send_all(self):
        msg_type = None
        time_stamp = time.time()
        seqno = len(self.window) + self.expected_ack
        while(len(self.window) < 5 and self.ifend == False):
            
            msg = self.infile.read(500)         # consider more appropriate size of pakage, utilize.
            if seqno == self.randstart:
                msg_type = 'start'
            elif msg == '':
                msg_type = 'end'
                self.ifend = True               # data transfer come to end, but resend could still happen.
                self.infile.close()
            else:
                msg_type = 'data'
            
            packet = self.make_packet(msg_type=msg_type, seqno=seqno, msg=msg)
            self.window.append([packet, 0, time_stamp])
            self.send(packet)
            print("send: %s", packet[0:20])

            seqno += 1

    def handle_timeout(self):
        time_stamp = time.time()
        if self.sack:
            self.send(self.window[0][0])
            print('sack resend: %s', self.window[0][0][0:20])
            self.window[0][2] = time_stamp
        else:
            for elem_index in range(len(self.window)):                          # gbn
                if (time_stamp > self.window[elem_index][2] + self.timeout):    # timeout
                    self.send(self.window[elem_index][0])
                    print('GBN resend: %s', self.window[elem_index][0][0:20])
                    self.window[elem_index][2] = time_stamp

    def handle_resp(self, recv):
        if Checksum.validate_checksum(recv):
            print("recv: %s" % recv)
            pieces = recv.split('|')
            ack = pieces[1]
            self.handle_ack(ack)
        else:
            print("recv: %s <--- CHECKSUM FAILED" % recv)

    def handle_ack(self, ack):
        pieces = ack.split(';')
        ack = int(pieces[0])
        assert(ack <= self.expected_ack + 5)
        ack_num = ack - self.expected_ack
        while(ack_num > 0):
            del self.window[0]
            ack_num -= 1
        self.expected_ack = max(ack, self.expected_ack)

    def log(self, msg):
        if self.debug:
            print(msg)


'''
This will be run if you run this script from the command line. You should not
change any of this; the grader may rely on the behavior here to test your
submission.
'''
if __name__ == "__main__":
    def usage():
        print("RUDP Sender")
        print("-f FILE | --file=FILE The file to transfer; if empty reads from STDIN")
        print("-p PORT | --port=PORT The destination port, defaults to 33122")
        print("-a ADDRESS | --address=ADDRESS The receiver address or hostname, defaults to localhost")
        print("-d | --debug Print debug messages")
        print("-h | --help Print this usage message")
        print("-k | --sack Enable selective acknowledgement mode")

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                               "f:p:a:dk", ["file=", "port=", "address=", "debug=", "sack="])
    except:
        usage()
        exit()

    port = 33122
    dest = "localhost"
    filename = None
    debug = False
    sackMode = False

    for o,a in opts:
        if o in ("-f", "--file="):
            filename = a
        elif o in ("-p", "--port="):
            port = int(a)
        elif o in ("-a", "--address="):
            dest = a
        elif o in ("-d", "--debug="):
            debug = True
        elif o in ("-k", "--sack="):
            sackMode = True

    s = Sender(dest, port, filename, debug, sackMode)
    try:
        s.start()
    except (KeyboardInterrupt, SystemExit):
        exit()
