import hashlib
import time

class Block:
    def __init__(self,block_id,data,timeS,previous_hash,nonce=0):
        self.nonce = nonce
        self.block_id = block_id
        self.transaction = data
        self.previous_hash=previous_hash
        self.timeS=timeS
        self.hash_of_data= self.create_hash_data()
        '''
        this won't be added in the headers
        '''
        self.my_hash = "0"
    

    def create_hash_data(self):
        data = str(self.transaction)
        return hashlib.sha256(data.encode()).hexdigest()
    
    def create_hash(self):
        hash_data = str(self.block_id) + str(self.hash_of_data) + str(self.previous_hash) +str(self.timeS) +str(self.nonce)
        self.my_hash= hashlib.sha256(hash_data.encode()).hexdigest()
    
        return self.my_hash

""""
this is the blockchain class
"""
class BlockChain:
    def __init__(self):
        self.chain = []
        self.unconfirmed_transaction=[]
        self.is_valid = False
        self.difficulty = 2
    
    
    def add_block(self,new_block,proof):
        prev_hash = self.get_latest_block().my_hash
        if prev_hash!=new_block.previous_hash:
            return False
        if not self.is_valid_proof(new_block,proof):
            return False
        
        new_block.my_hash = proof
        print (proof)
        self.chain.append(new_block)
        return True
    
    """a dummy block       """
    def create_genesis_block(self):
            genesis_block = Block(0,[],0,"0")
            genesis_block.my_hash = genesis_block.create_hash()
            self.chain.append(genesis_block)

    
    def proof_of_work(self,block):
        block.nonce= 0
        target = "0" * self.difficulty
        computed_hash = block.create_hash()

        while computed_hash[:2]!=target:
            block.nonce += 1
            computed_hash= block.create_hash()
        
        return computed_hash
    

    def is_valid_proof(self,block,block_hash):
        print("hello2")
        print("hash", block_hash==block.create_hash())
        print(block_hash[:2])
        return (block_hash[:2]=="0"*self.difficulty and block_hash==block.create_hash())

    def get_latest_block(self):
        return self.chain[-1]
    

    """this function will be called when nodes are joined first"""
    def get_the_longest_chain(self, length,chain):
        """
        we need to check if the chain makes sense
        
        """
        chain_temp =[]
        for i in chain:
            block = Block(i["block_id"],
                          i["transaction"],
                          i["timeS"],
                          i["previous_hash"],
                          i["nonce"]
                          )
            block.my_hash=i["my_hash"]
            block.hash_of_data=i["hash_of_data"]
            chain_temp.append(block)

        
        longest_chain = None
        current_len = len(self.chain)
        if  length > current_len and self.check_chain_validity(chain_temp):

            current_len = length
            longest_chain=chain
        
        if longest_chain:
            chain = longest_chain
            return True
        
        return False
    

    def check_chain_validity(self,chain):
        print("hello")
        res= True
        previous_hash = "0"
        for block in chain:
            """indicate the genesis block"""
            if block.block_id==0:
                previous_hash = block.my_hash
                continue

            if not self.is_valid_proof(block,block.my_hash) or previous_hash!=block.previous_hash:
                res= False
                break
            previous_hash = block.my_hash
        return res
    


    #this function will deal with if there is a block from the 
    def verify_add_data(self, block_data):
        #create the block
        block = Block(block_data["block_id"],
                      block_data["transaction"],
                      block_data["timeS"],
                      block_data["previous_hash"],
                      block_data["nonce"]
                      ) #todo
        proof = block_data["my_hash"]
        added= self.add_block(block,proof)
        if not added:
            return False
        else:
            return True
    
    def add_new_transaction(self,transaction):
        """
        json query
        """
        self.unconfirmed_transaction.append(transaction)

    def mining(self):
        """if the above funnction returned true then broadcast the last node to the all peers"""
        if not self.unconfirmed_transaction:
            return False
        else:
            last_block = self.get_latest_block()
            prev_hash = last_block.my_hash 
            print("previous_hash is",prev_hash)
            block = Block(last_block.block_id+1, 
                          self.unconfirmed_transaction,
                          timeS=time.time(),previous_hash=prev_hash)
            proof = self.proof_of_work(block)
            self.add_block(block,proof)
            self.unconfirmed_transaction=[]
            return True
        
    """if the above funnction returned true then broadcast"""
'''

if __name__=='__main__':
    blokChain = BlockChain()
    blokChain.create_genesis_block()
    print(blokChain.get_latest_block().transaction)
    tranaction = {
                  "voter_id":"x",
                  "name" : "john"
                  }
    blokChain.add_new_transaction(tranaction)
    res = blokChain.mining()
    print(res)

    tranaction2 = {
                  "voter_id":"x",
                  "name" : "john Doe"}
    chains=[]
    for block in blokChain.chain:
        chains.append(block.__dict__)
    print(chains)

'''

    
   











