import datetime
from blockchain import Block, BlockChain
from peer import Peers
class Vote:
    def __init__(self, vote_id, vote_data):
        self.vote_id = vote_id
        self.vote_data = vote_data
        self.timeS = datetime.datetime.now()
        self.block = Block(vote_id, vote_data, self.timeS)
        self.blockchain = BlockChain()
        self.blockchain.add_block(self.block)
        self.is_valid = self.blockchain.is_valid_block(self.block)

    def __str__(self):
        return f"Vote ID: {self.vote_id}, Vote Data: {self.vote_data}, Time: {self.timeS}, Block: {self.block}, Blockchain: {self.blockchain}, Is Valid: {self.is_valid}"
    
class VoteChain:
    def __init__(self):
        self.vote_chain = []
        # self.peers = Peers(5000)
    
    def add_vote(self, vote):
        self.vote_chain.append(vote)
        self.peers.p2pclient()
    
    def __str__(self):
        return f"Vote Chain: {self.vote_chain}"
    
    def get_votes(self):
        return self.vote_chain
    
    def get_results(self):
        results = {}
        for vote in self.vote_chain:
            if vote.vote_data not in results:
                results[vote.vote_data] = 0
            results[vote.vote_data] += 1
        return results
    
class VoteChainError(Exception):
    #TODO: Implement this class
    pass