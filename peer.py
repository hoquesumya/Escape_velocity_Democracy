from socket import *
import argparse
import json
import threading
import time
import collections
from blockchain import BlockChain


all_peers_list=set()
lock = threading.Lock()



def p2pclient(blockChain):
        """
        this function 
        inititates the peer client which will be 
        called first when a peer joins to the network
        upon joining the network this
        function will requests the other peers to get the longest chain
        in order to be synced
        """
        i = 0
        #this loops waits for a few bit to get the peer_list. Immportant for the first peer in net
        while (not all_peers_list and i<3):

            print("Waiting for peers to become available...")
            i+=1
            time.sleep(1)
    
        print("all peers are",all_peers_list)
       
        # connect to peers and get the chain
        lock.acquire()
        
        for i in all_peers_list:
            get_init_blockchain(i,blockChain)

        lock.release()
        print(blockChain.get_all_chain())

def get_init_blockchain(i,blockChain):
            """
            this function will request to the connected peers 
            to retrieve the blockchain from the peers
            and then copare if the exsting chain is > recently retrieved list
            if it is, then update the chain 

            """
            buffer = 1024
            temp_client_sock = socket(AF_INET, SOCK_STREAM)
            print("my peer is",i)
            temp_client_sock.connect((i[0],i[1]))

            temp_data = ""
            print("sending now")
            data = {
                "msg_type":"needBlockchain"
            }
            data1=json.dumps(data)
            temp_data+=data1
            temp_data+="done"
            temp_client_sock.send(temp_data.encode())

            temp_data = ""
            while True:
                data = temp_client_sock.recv(buffer).decode()
                #print(data)
                temp_data += data
                if "done" in temp_data:
                  temp_data = temp_data.replace("done", "")
                  break

            
            temp = json.loads(temp_data)
            #update the chain ased on the length
            res  = blockChain.get_the_longest_chain(temp["len"],temp["chain"])
            print("longest_chain is",res)
            temp_client_sock.close()


def get_chain_and_send(clientsoc,blockChain):
    """
    this function is for the peers who get the request from the other peer
    to get the blockchain for that.
    the blockchainsa are semd as __dict__ over the network
    """
    chains = []
    for block in blockChain.chain:
        chains.append(block.__dict__)

    data = {
        "len":len(chains),
        "chain":chains
    }
    data1 = json.dumps(data)
    data_temp  = ""
    data_temp += data1
    data_temp += "done"

    clientsoc.sendall(data_temp.encode())

class Peers:
    """
    this class is core to establish p2p arch.

    p2p works both as a server and the client
    it deals with the tracker to retrieve the peer_list in every 10
    then accpet connection from clients and the other peers

    """
    def __init__(self,port,blockchain):

        self.myPeers=set()
        self.peerSock=socket(AF_INET, SOCK_STREAM)
        self.peerSockserver =  socket(AF_INET,SOCK_STREAM)
        self.port = port
    
        self.temp = []
        ip_address = gethostname()
        self.ip=str(gethostbyname(ip_address))
        self.blockChain = blockchain

    def mine_unverified_transaction(self, clientsoc):
        """
        this function will mine the unverified transaction
        and add to the blockchain by calling blockchain function
        broadcast the block to the peer so that they are in sync
        if valid block, send client 200 status

        """
        global all_peers_list
        #mine the unverified transaction and add to block
        result = self.blockChain.mining()
        response = {
            "status":200
        }
        if not result:
            response={
                "status":400
            }

        else:
            #after adding the block print the blockchain
            print("my chain is", self.blockChain.get_all_chain())
            lock.acquire()

            succ_count = 0
            fail_count = 0

           # print("my peers are", all_peers_list)
            """get alll peers and connect to the peeer to brpadcast to the added block to them"""
            for peers in all_peers_list:
                print("sending the data to",peers)
                temp_client_sock = socket(AF_INET, SOCK_STREAM)
                temp_client_sock.connect((peers[0],peers[1]))
                block=self.blockChain.get_latest_block()
                block1 = block.__dict__
               
                data = {
                    'msg_type':"incoming_block",
                    "data":block1
                }
                data1= json.dumps(data)
                temp_data = ""
                temp_data+=data1
                temp_data+="done"
                temp_client_sock.sendall(temp_data.encode())
                while True:
                    data = temp_client_sock.recv(1024).decode()
                    if "done" in data:
                        # Remove 'done' and any extraneous characters beyond it
                        data = data.split("done")[0]

                    print("received status is",data)
                    try:
                        data = json.loads(data)
                    
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON: {e}")

                    if data["status"] == 200:
                        print("a valid block from the peer")
                        succ_count+=1
                    else:
                        fail_count+=1
                    break
                temp_client_sock.close()
            lock.release()
        #send the response to the client if the transaction is valid
        response1= json.dumps(response)
        clientsoc.sendall(response1.encode())


    def handleTracker(self, trackerPort, trackerIp):
        """
        will recv and send from /to the tracker
        "registering with the tracker
        unregistering with the tracker
        periodically communicate with the tracker to get the updates of 
        the alive peers
        """
        addr = {
            "action":"register",
            "ip":self.ip,
            "port":self.port
        }

        addr_str = json.dumps(addr)

        self.peerSock.connect((trackerIp,trackerPort))
        addr1 = {
            "ip":self.ip,
            "port":self.port
        }

        self.peerSock.sendall(addr_str.encode())
        
        buffer = 1024
        while True:
            #periodically send the request to the tracker to get the update
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
                    if item!=addr1:
                        lock.acquire()
                        all_peers_list.add((item["ip"],item["port"]))
                        lock.release()
                    print("list is", all_peers_list)
            except timeout:
               
                self.peerSock.sendall(addr_str.encode())
                continue
           

    def p2p_server(self):
        """
        will act as a server and listen for the incoming connection from the other peers
        and the client
        will differentaite betweeen the request_type by indentifying ["msg_type"]


        """

        self.peerSockserver.bind(('',self.port))
        self.peerSockserver.listen(1)
        buffer_size = 1024
        while True:
            print("Accepting connections...")
            temp_data1 = ""
            temp2      = None
            clientsoc, addr =self.peerSockserver.accept()
            print(addr)
            while True:
                data = clientsoc.recv(buffer_size)
                if not data:
                        print("Data receieved successfully")
                        break
                temp_data1+=data.decode()
                #print("data",data)
               
                if "done" in temp_data1:
                  temp2 = temp_data1.split("done")
                  break

            
            temp_data2 = json.loads(temp2[0])
            #print("temp_data",temp_data2)

            ''' newly connected peer wants to have the copy of the blockchain'''
            if temp_data2["msg_type"] == "needBlockchain":
                print("sending the blockchain to the peer")
                   # clientsoc.sendall(b'sent all the blockchains')
                get_chain_and_send(clientsoc=clientsoc,blockChain=self.blockChain)

            elif temp_data2["msg_type"] == "get_results":
                """
                this will send the vote results to the client
                """
                self.send_vote_results_to_client(clientsoc)

            elif temp_data2["msg_type"] == "incoming_block":
                    """
                     this  part will handle validating the block
                     if the block is valid will be added to the chain and will perform mining
                     then send the success status
                    """
                    print("Received block from peer. Validating...")
                    
                    send_data = {}
                    temp = temp_data2["data"]
                    #print("temp is", temp)
                    res = self.blockChain.verify_add_data(temp)

                    if res == False:
                        send_data = {
                            "status":500
                        }

                    
                    else:
                        print("Valid block received. Adding to chain...")
                        send_data = {
                            "status":200
                         }
                        print("I am another peer and my chain is",
                              self.blockChain.get_all_chain())

                    send_data1 = json.dumps(send_data)              
                    clientsoc.sendall(send_data1.encode())

            
            elif temp_data2["msg_type"]=="request_blockchain":
                 self.send_blockchain_json_object(clientsoc)
                        
                    
            else:
                    """
                    this part deals with the client request
                    newly traansaction will be added to the unverified_transaaction array
                    then miner will pick that data from the array
                    """
                    self.blockChain.add_new_transaction(temp_data2)
                    self.mine_unverified_transaction(clientsoc)
         
                
            clientsoc.close()
    

    def send_blockchain_json_object(self, clientsoc):
        """
        send the blockchain to the client for visualization
        """
        chains = []
        for block in self.blockChain.chain:
            chains.append(block.__dict__)
        data = {"len": len(chains), "chain": chains}
        data1 = json.dumps(data)
        data_temp = data1 + "done"
        clientsoc.sendall(data_temp.encode())

    def send_vote_results_to_client(self, clientsoc):
        """
        Sends the frequency of each vote value on the blockchain. Handles transactions that may be
        either a single dictionary or a list of dictionaries.
        """
        data = {}
        # Loop through each block in the blockchain
        for block in self.blockChain.chain:
            # Handle both single transaction dictionary and list of transactions
            transactions = block.transaction if isinstance(block.transaction, list) else [block.transaction]
            # Aggregate votes from transactions
            for transaction in transactions:
                if 'vote' in transaction:  # Check if 'vote' key exists in transaction
                    vote = transaction['vote']
                    if vote not in data:
                        data[vote] = 1
                    else:
                        data[vote] += 1

        # Prepare the data for sending
        data_json = json.dumps(data) + "done"

        print(f"Sending vote results to client: {data_json}")
        clientsoc.sendall(data_json.encode())

    



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
    #intitiats the blockchain class and create the genesis block and add to the chain
    blockChain = BlockChain()
    blockChain.create_genesis_block()
  

    peer=Peers(peerPort,blockChain)
    #first registerwith the tracker and get all the avaliable tracker
    all_threads = []

    t = threading.Thread(target=peer.handleTracker, args=(trackerPort,trackerIp,))
    t.start()
    all_threads.append(t)


    p2pclient(blockChain=blockChain)
        
    t2 = threading.Thread(target=peer.p2p_server, args=())
    t2.start()
    all_threads.append(t2)
    
