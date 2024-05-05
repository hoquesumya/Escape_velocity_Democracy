import hashlib


class Block:
    def __init__(self,block_id,data,timeS):
        self.nonce = 0
        self.block_id = block_id
        self.transaction = data
        self.previous_block=None
        self.timeS=timeS
        self.hash_of_data= self.create_hash_data()
        '''
        this won't be added in the headers
        '''
        self.my_hash = self.create_hash_block()
    

    def create_hash_data(self):
        data = str(self.transaction)
        return hashlib.sha256(data.encode()).hexdigest()
    
    def create_hash_block(self):
        hash_data = str(self.block_id) + str(self.hash_of_data) + str(self.previous_block) +str(self.timeS) +self.nonce()
        self.my_hash= hashlib.sha256(hash_data()).hexdigest()
        target = "0" * 2
        '''
        mining process; probably put in the different function
        '''
        while self.create_hash_data[:2]!=target:
            self.nonce += 1
            hash_data = str(self.block_id) + str(self.hash_of_data) + str(self.previous_block) +str(self.timeS) +self.nonce()
            self.my_hash= hashlib.sha256(hash_data()).hexdigest()
        return self.my_hash





""""
this is the blockchain class
"""

class BlockChain:
    def __init__(self):
        self.chain = []
        self.is_valid = False
    
    def add_block(self,new_block):
        new_block.previous_block = self.get_latest_block().my_hash
        self.chain.append(new_block)

    
    def is_valid_block(self,new_block):
        """
        check the nonce and the transaction types
        """
        pass








