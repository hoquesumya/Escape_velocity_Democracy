from socket import *
import argparse
import json
import threading
class Peers:
    def __init__(self,port):
        self.myPeers=set()
        self.peerSock=socket(AF_INET, SOCK_STREAM)
        self.peerSockserver =  socket(AF_INET,SOCK_STREAM)
        self.all_peers_list=set()
        self.port = port
        self.lock = threading.Lock()
        ip_address = gethostname()
        self.ip=str(gethostbyname(ip_address))

    def handleTracker(self, trackerPort, trackerIp):
        """
        will recv and send from /to the tracker
        "registering with the tracker
        unregistering with the tracker
        periodically communicate with the tracker to get the updates of 
        the alive tracker
        """
        addr = {
            "ip":self.ip,
            "port":self.port
        }
        addr_str = json.dumps(addr)
        self.peerSock.connect((trackerIp,trackerPort))

        self.peerSock.sendall(addr_str.encode())
        
        buffer = 1024
        while True:
            self.peerSock.settimeout(10)
            try:
                data = self.peerSock.recv(buffer)
                data = data.decode()
                data=data.split('\n')

                for i in data:
                    print(i)
                    if not i:
                        continue
                    item = json.loads(i)
                    print (item)
                    if item!=addr:
                        self.lock.acquire()
                        self.all_peers_list.add((item["ip"],item["port"]))
                        self.lock.release()
                        print("list is", self.all_peers_list)
            except timeout:
                self.peerSock.sendall(addr_str.encode())
                continue

    def p2p_server(self):
        """
        will act as a server and listen for the incoming connection from the other peers
        """

        self.peerSockserver.bind(('',self.port))
        self.peerSockserver.listen(1)
        buffer_size=1024
        while True:
            print("accepting again")
            clientsoc, addr =self.peerSockserver.accept()
            print(addr)
            while True:
                data = clientsoc.recv(buffer_size)
                if not data:
                        print("data is done")
                        break
                data=data.decode()
                print(data)
                clientsoc.sendall(b'hello')
                break

    def p2pclient(self):
        #will act as a client
        #first initally send request to the other server to get the copy of the blockchain
        """
        case 1:
        no known peers available; wait for other thread to handle that
        case 2:
        PEERS are here; but i don't have any block request for block
        case 3: I have a new transaction broadcast to the other peers
        """
        buffer = 1024
        while (not self.all_peers_list): # modify this
            print("waitng for peers to be available")
        #send the all peers to get the initial block
        print("ip's are available")
        #multipl client multiple socet
        all_client_sock = []
        for i in self.all_peers_list:
            temp_client_sock = socket(AF_INET, SOCK_STREAM)
            all_client_sock.append(temp_client_sock)
            print("my peer is",i)
            temp_client_sock.connect((i[0],i[1]))
        
        for i in all_client_sock:
            
            data = i.recv(buffer)
            data = data.decode()
            print(data)
            
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
    all_threads = []

    t = threading.Thread(target=peer.handleTracker, args=(trackerPort,trackerIp,))
    t.start()
    all_threads.append(t)
    t1 = threading.Thread(target=peer.p2pclient, args=())
    t1.start()
    all_threads.append(t1)
    t2 = threading.Thread(target=peer.p2p_server, args=())
    t2.start()
    all_threads.append(t2)

    #peer.handleTracker(trackerPort,trackerIp)


    