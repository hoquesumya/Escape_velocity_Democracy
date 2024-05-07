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
    
        all_threads = []
        i = 0
        while (not all_peers_list and i<3):
            print("waitng for peers to e available")
            i+=1
            time.sleep(1)
        #send the all peers to get the initial block
        print("ip's are available")
        #multipl client multiple socet
        lock.acquire()

        for i in all_peers_list:
            get_init_blockchain(i,blockChain)
           # self.lock.acquire()
        lock.release()
        print(blockChain.get_all_chain())

def get_init_blockchain(i,blockChain):
            buffer = 1024
            temp_client_sock = socket(AF_INET, SOCK_STREAM)
            print("my peer is",i)
            temp_client_sock.connect((i[0],i[1]))
            #self.lock.release()
            temp_data = ""
            print("sending now")
            data = {
                "msg_type":"needBlockchain"
            }
            data1=json.dumps(data)
            temp_data+=data1
            temp_data+="done"
            temp_client_sock.send(temp_data.encode())
            print("connecting to the  peer")
            temp_data = ""
            while True:
                data = temp_client_sock.recv(buffer).decode()
                #print(data)
                temp_data += data
                if "done" in temp_data:
                  temp_data = temp_data.replace("done", "")
                  break
            #print(temp_data)
            
            temp = json.loads(temp_data)
            res  = blockChain.get_the_longest_chain(temp["len"],temp["chain"])
            print("logest_chain is",res)
            temp_client_sock.close()

    

def get_chain_and_send(clientsoc,blockChain):
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
        """
        global all_peers_list
        result = self.blockChain.mining()
        response = {
            "status":200
        }
        if not result:
            response={
                "status":400
            }

        else:
            print("my chain is", self.blockChain.get_all_chain())
            lock.acquire()

            succ_count = 0
            fail_count = 0
            print("my peers are", all_peers_list)
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

        response1= json.dumps(response)
        clientsoc.sendall(response1.encode())


    def handleTracker(self, trackerPort, trackerIp):
        """
        will recv and send from /to the tracker
        "registering with the tracker
        unregistering with the tracker
        periodically communicate with the tracker to get the updates of 
        the alive tracker
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
        """

        self.peerSockserver.bind(('',self.port))
        self.peerSockserver.listen(1)
        buffer_size = 1024
        while True:
            print("accepting again")
            temp_data1 = ""
            temp2      = None
            clientsoc, addr =self.peerSockserver.accept()
            print(addr)
            while True:
                data = clientsoc.recv(buffer_size)
                if not data:
                        print("data is done")
                        break
                temp_data1+=data.decode()
                #print("data",data)
               
                if "done" in temp_data1:
                  temp2 = temp_data1.split("done")
                  break

            
            temp_data2 = json.loads(temp2[0])
            #print("temp_data",temp_data2)

            '''newly connected peer wants to have the copy of the blockchain'''
            if temp_data2["msg_type"] == "needBlockchain":
                print("hello")
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
                    print("found data")
                    
                    send_data = {}
                    temp = temp_data2["data"]
                    #print("temp is", temp)
                    res = self.blockChain.verify_add_data(temp)

                    if res == False:
                        send_data = {
                            "status":500
                        }

                    
                    else:
                        print("yay, i got a valid block")
                        send_data = {
                            "status":200
                         }
                        print("i am other peer and my updated chain is",self.blockChain.get_all_chain())

                    send_data1 = json.dumps(send_data)              
                    clientsoc.sendall(send_data1.encode())

            
            elif temp_data2["msg_type"]=="request_blockchain":
                 self.send_blockchain_json_object(clientsoc)
                        
                    
            else:
                   
                    print(data)
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
    '''
    
    def check_chain_validity_for_tampering(self):
        """
        this function will check if block has been tempered. if so will go for the longest 
        chain
        """
        
        interval = 60

        time.sleep(interval)

        while len(self.blockChain.chain>1):
             res = self.blockChain.validate_chain()
             if res == False:
                  p2pclient()
             time.sleep(interval)
             
    '''
    



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
    
    '''
    
    t2 = threading.Thread(target=peer.check_chain_validity_for_tampering, args=())
    t2.start()
    all_threads.append(t2)

    '''