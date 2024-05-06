## PROJECT IDEAS:

- What if we lived in a world without a centralized government? And all decisions were voted on by the population. The results of these votes would be extremely sensitive, so we can’t trust any individual to store it in its entirety. We propose a protocol to support Blockchain Voting Ledger for Direct Democracy


## FEATURES:
Our project will be split up into two sections: 1. an internet protocol to handle voting and guard against fraud 2. A blockchain implementation that stores the ballots and their anonymized results.
1. Protocol Layer

2. Blockchain Layer
## Apportionment of Tasks:
Since we are a small team of two people (our assigned teammate Run is AWOL), we will divide the labor according to the above-mentioned sections. Caspar will lead the development of the protocol layer, and Sumya will handle the blockchain implementation. 

## p2pserver():
    1. client/ peer will connect to the peer server. 
    2. differentiate the request type: 
        - client request
            -  Block(block_id,client_side_data, timestamp)
            - put the block to the queue so that the p2pclient can grab the block
        - peer request:
            1. to get the all copy of the blockchain
                - send the blockchain to the connected peer
            2. incoming new block from a peer
                - need to validate the block. After validation send status;
                - if block is validated, add the block to the chain

##  p2pclient(self):
    1. new peer
        - request for the blockcain list to all its peer (get from tracker)
        - if there is only one peer; the peer will wait for couple of seconds to have other peers
          if not found, than the loop won't be executed: 
          ```python
            
            for i in self.all_peers_list:
                
                t = threading.Thread(target=self.init_blockchain, args=(i,))
                t.start()
                all_threads.append(t)
            ```
        - if there are other peers, the loop will be executed, and after the execution
        the p2pclient will check which peer has the largest block_id will accept that blockchain

    2.both old and new peer will check  ```self.enqueue = collections.deque()``` to get the newly created block from p2pserver(). 
        - if block exists, popleft() from enqueue; and broadcast to exisiting peers to get the validation. If maximum peers accepts the blockchain; add the block to the blockain
            
