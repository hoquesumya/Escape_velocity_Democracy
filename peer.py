from socket import *
import argparse

class Peers:
    def __init__(self,port):
        self.myPeers=set()
        self.peerSock=socket(AF_INET, SOCK_STREAM)


    def handleTracker(self, trackerPort, trackerIp):
        """
        will recv and send from /to the tracker
        "registering with the tracker
        unregistering with the tracker
        periodically communicate with the tracker to get the updates of 
        the alive tracker
        """
        self.peerSock.connect((trackerIp,trackerPort))
        self.peerSock.sendall(b'hello')
        
        buffer = 1024
        while True:
            data = self.peerSock.recv(buffer)
            data = data.decode()
            print(data)
    
    def p2pcommunication():
        pass


if __name__=='__main__':
    parser = argparse.ArgumentParser(
                    prog='tracker.py',
                    description='tracker.py simulates the network. It forwards data between the server/client programs and varies link conditions to test your implementation of the rate adaptation algorithm in the client.')
    parser.add_argument('peerPort', type=int, choices=range(49151,65535), metavar='trackerPort: (49151-65535)')
    #tracker address
    parser.add_argument('trackerAddr', type=str)
    parser.add_argument('trackerPort', type=int, choices=range(49151,65535), metavar='trackerPort: (49151-65535)')
    args = parser.parse_args()
    peerPort = args.peerPort
    trackerIp = args.trackerAddr
    trackerPort= args.trackerPort
    peer=Peers(peerPort)
    #first registerwith the tracker and get all the avaliable tracker
    peer.handleTracker(trackerPort,trackerIp)


    