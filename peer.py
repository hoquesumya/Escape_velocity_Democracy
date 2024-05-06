import argparse
import collections
import json
import threading
import time
from socket import *  # noqa: F403

from blockchain import BlockChain

def get_chain_and_send(clientsoc, blockChain):
    chains = []
    for block in blockChain.chain:
        chains.append(block.__dict__)
    data = {"len": len(chains), "chain": chains}
    data1 = json.dumps(data)
    data_temp = data1 + "done"
    clientsoc.sendall(data_temp.encode())


class Peers:
    def __init__(self, port, blockchain):
        self.myPeers = set()
        self.peerSock = socket(AF_INET, SOCK_STREAM)
        self.peerSockserver = socket(AF_INET, SOCK_STREAM)
        self.all_peers_list = set()
        self.port = port
        """this is the list of locking to handle multiple scenrios"""
        self.lock = threading.Lock()
        self.lock_blockchain = threading.Lock()
        self.temp_block = threading.Lock()
        self.temp = []
        ip_address = gethostname()
        self.ip = str(gethostbyname(ip_address))
        self.enqueue = collections.deque()
        self.blockChain = blockchain

    def mine_unverified_transaction(self, clientsoc):
        """
        this function will mine the unverified transaction
        """
        result = self.blockChain.mining()
        response = {"status": 200}
        if not result:
            response = {"status": 400}

        else:
            self.lock.acquire()
            succ_count = 0
            fail_count = 0
            for peers in self.all_peers_list:
                temp_client_sock = socket(AF_INET, SOCK_STREAM)
                temp_client_sock.connect((peers[0], peers[1]))
                block = self.blockChain.get_latest_block()
                print("the latest block is", block)
                block1 = block.__dict__
                temp_client_sock.sendall(block1.encode())
                while True:
                    data = temp_client_sock.recv(1024).decode()
                    data = json.loads(data)
                    if data["staus"] == 200:
                        succ_count += 1
                    else:
                        fail_count += 1
                    break

        response1 = json.loads(response)
        clientsoc.sendall(response1.encode())

    def handleTracker(self, trackerPort, trackerIp):
        """
        will recv and send from /to the tracker
        "registering with the tracker
        unregistering with the tracker
        periodically communicate with the tracker to get the updates of
        the alive tracker
        """
        addr = {"action": "register", "ip": self.ip, "port": self.port}
        addr_str = json.dumps(addr)
        self.peerSock.connect((trackerIp, trackerPort))
        addr1 = {"ip": self.ip, "port": self.port}

        self.peerSock.sendall(addr_str.encode())

        buffer = 1024
        while True:
            self.peerSock.settimeout(10)
            try:
                data = self.peerSock.recv(buffer)
                data = data.decode()
                data = data.split("\n")

                for i in data:
                    print(i)
                    if not i:
                        continue
                    item = json.loads(i)
                    print(item)
                    if item != addr1:
                        self.lock.acquire()
                        self.all_peers_list.add((item["ip"], item["port"]))
                        self.lock.release()
                        print("list is", self.all_peers_list)
            except timeout:
                self.peerSock.sendall(addr_str.encode())
                continue

    def p2p_server(self):
        """
        will act as a server and listen for the incoming connection from the other peers
        """

        self.peerSockserver.bind(("", self.port))
        self.peerSockserver.listen(1)
        buffer_size = 1024
        while True:
            print("accepting again")
            clientsoc, addr = self.peerSockserver.accept()
            print(addr)
            while True:
                data = clientsoc.recv(buffer_size)
                if not data:
                    print("data is done")
                    break
                data = data.decode()
                data = json.loads(data)
                print("recvd data is", data)

                """newly connected peer wants to have the copy of the blockchain"""
                if data["msg_type"] == "needBlockchain":
                    # clientsoc.sendall(b'sent all the blockchains')
                    get_chain_and_send(clientsoc=clientsoc, blockChain=self.blockChain)

                elif data["msg_type"] == "incoming_block":
                    """
                     this  part will handle validating the block
                     if the block is valid will be added to the chain and will perform mining
                     then send the success status
                    """
                    send_data = {}
                    res = self.blockChain.verify_add_data()
                    if res == False:
                        send_data = {"status": 500}
                        send_data1 = json.dumps(send_data)
                        clientsoc.sendall(send_data1.encode())

                else:
                    """
                    client request
                    create the block
                    append to the enquue
                    self.lock_blockhain.acquire()
                    self.enqueue.append(block)
                    self.lock_blockchain.release()
                    """
                    self.blockChain.add_new_transaction(data)
                    self.mine_unverified_transaction(clientsoc)
                    clientsoc.sendall(b"added to the queue")
                    print("added to the queue")
                    clientsoc.close()

                break

    def get_init_blockchain(self, i, blockChain):
        buffer = 1024
        temp_client_sock = socket(AF_INET, SOCK_STREAM)
        print("my peer is", i)
        temp_client_sock.connect((i[0], i[1]))
        # self.lock.release()

        print("sending now")
        data = {"msg_type": "needBlockchain"}
        data1 = json.dumps(data)

        temp_client_sock.send(data1.encode())
        print("connecting to the peer")
        temp_data = ""
        while True:
            data = temp_client_sock.recv(buffer).decode()
            # print(data)
            temp_data += data
            if "done" in temp_data:
                temp_data = temp_data.replace("done", "")
                break
        # print(temp_data)

        temp = json.loads(temp_data)
        self.lock_blockchain.acquire()
        res = blockChain.get_the_longest_chain(temp["len"], temp["chain"])
        print("logest_chain is", res)
        self.lock_blockchain.release()
        temp_client_sock.close()

    def p2pclient(self):
        # will act as a client
        # first initally send request to the other server to get the copy of the blockchain
        """
        case 1:
        no known peers available; wait for other thread to handle that
        case 2:
        PEERS are here; but i don't have any block request for block
        case 3: I have a new transaction broadcast to the other peers
        """
        all_threads = []
        i = 0
        while not self.all_peers_list and i < 3:
            print("waitng for peers to e available")
            i += 1
            time.sleep(1)
        # send the all peers to get the initial block
        print("ip's are available")
        # multiple client multiple socket

        self.lock.acquire()
        """
        this loop is for getting intial blockchain from the peers
        Note: at first there could be no other peers than the all_peers_list
        will be empty; and this loop won't be executed
        """
        for i in self.all_peers_list:
            t = threading.Thread(
                target=self.get_init_blockchain, args=(i, self.blockChain)
            )
            t.start()
            all_threads.append(t)
        # self.lock.acquire()
        self.lock.release()

        # compare temp which block has the highest id accept that block

        """
        after comparing the blockchain start reviewing the client transaction from the enqueue
        """

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="tracker.py",
        description="tracker.py simulates the network. It forwards data between the server/client programs and varies link conditions to test your implementation of the rate adaptation algorithm in the client.",
    )
    parser.add_argument(
        "peerPort",
        type=int,
        choices=range(49151, 65535),
        metavar="trackerPort: (49151-65535)",
    )
    # tracker address
    parser.add_argument("trackerAddr", type=str)
    parser.add_argument(
        "trackerPort",
        type=int,
        choices=range(49151, 65535),
        metavar="trackerPort: (49151-65535)",
    )
    args = parser.parse_args()
    peerPort = args.peerPort
    trackerIp = args.trackerAddr
    trackerPort = args.trackerPort

    blockChain = BlockChain()
    blockChain.create_genesis_block()

    peer = Peers(peerPort, blockChain)
    # first register with the tracker and get all the avaliable tracker
    all_threads = []

    t = threading.Thread(
        target=peer.handleTracker,
        args=(
            trackerPort,
            trackerIp,
        ),
    )
    t.start()
    all_threads.append(t)
    t1 = threading.Thread(target=peer.p2pclient, args=())
    t1.start()
    all_threads.append(t1)

    t2 = threading.Thread(target=peer.p2p_server, args=())
    t2.start()
    all_threads.append(t2)

    # peer.handleTracker(trackerPort,trackerIp)

# tests using pytest
def test_get_chain_and_send():
    blockChain = BlockChain()
    blockChain.create_genesis_block
    blockChain.mining()
    assert len(blockChain.chain) == 2

def test_mine_unverified_transaction():
    blockChain = BlockChain()
    blockChain.create_genesis_block
    blockChain.mining()
    assert len(blockChain.chain) == 2
    peer = Peers(5000, blockChain)
    peer.mine_unverified_transaction()
    assert len(blockChain.chain) == 3

