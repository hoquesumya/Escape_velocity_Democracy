"""
this file will work as the server where it will send theactive peer list to the peers
also handles the peer notification of joining and leavingthe network
"""
from socket import *
import argparse
import threading
import json

class Tracker:
    def __init__(self):
        """
        multi-threaded trackers
        """
        self.active_peers=set()
        self.t=None
        self.s=None
        self.stop_event = threading.Event()

    def handlePeersConnections(self,clientsoc,addr):
        """
        based on the data typ
        """
        buffer_size =1024
        try:
            while not self.stop_event.is_set():
                    data = clientsoc.recv(buffer_size)
                    if not data:
                        print("daa is done")
                        """remove the ip and port from the set of the peer"""
                        break
                    data = data.decode()
                    data = json.loads(data)

                    if ((data["ip"], data["port"])) not in self.active_peers:
                        self.active_peers.add((data["ip"], data["port"]))
                    
                    self.update_peers(clientsoc)
    
        finally:
            clientsoc.close()

    def update_peers(self,clientsoc):
       
       for i in self.active_peers:
            sending_data = json.dumps({"ip":i[0], "port":i[1]})
            sending_data+='\n'
            clientsoc.sendall(sending_data.encode())

  
        
    def start_tracker(self,trackerPort):
        self.s = socket(AF_INET,SOCK_STREAM)
        self.s.bind(('',trackerPort))
        self.s.listen(1)
        threads=[]
        try:
            while True:
                print("accepting again")
                clientsoc, addr =self.s.accept()
                print(addr)
                self.t = threading.Thread(target=self.handlePeersConnections, args=(clientsoc,addr,))
                self.t.start()
                threads.append(self.t)
        except KeyboardInterrupt:
            print("keyboard interrupted")
            self.stop_event.set()
            for t in threads:
                t.join()
            self.s.close()
    


if __name__=='__main__':
    parser = argparse.ArgumentParser(
                    prog='tracker.py',
                    description='tracker.py simulates the network. It forwards data between the server/client programs and varies link conditions to test your implementation of the rate adaptation algorithm in the client.')
    parser.add_argument('trackerPort', type=int, choices=range(49151,65535), metavar='trackerPort: (49151-65535)')
    args = parser.parse_args()
    trackerPort = args.trackerPort
    tracker = Tracker()
    tracker.start_tracker(trackerPort)
