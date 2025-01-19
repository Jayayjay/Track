import hashlib
import time

class Block:
    def __init__(self, data, previous_hash):
        self.timestamp = time.time()
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()
    
    def calculate_hash(self):
        # You'll recognize this string encoding from Python
        block_content = str(self.timestamp) + str(self.data) + str(self.previous_hash)
        return hashlib.sha256(block_content.encode()).hexdigest()