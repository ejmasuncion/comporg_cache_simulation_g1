# logic/lru.py

# Step through cache,  feature

class FACacheSimulator:
    def __init__(self, words_per_block, num_blocks, hit_time, miss_time):
        self.words_per_block = words_per_block
        self.num_blocks = num_blocks
        self.hit_time = hit_time
        self.miss_time = miss_time
        
        self.cache = [] # List of dicts: {'Block': tag, 'Age': time}
        self.timer = 0
        self.access_count = 0
        self.hit_count = 0
        self.miss_count = 0
        self.trace_log = []

    def access(self, word_address):
        self.timer += 1
        self.access_count += 1
        block_tag = word_address // self.words_per_block
        
        # Check Hit
        for entry in self.cache:
            if entry['word_address'] == word_address:
                entry['Age'] = self.timer
                entry['word_address'] = word_address
                self.hit_count += 1
                self.trace_log.append(f"HIT: Word {word_address} (Blk {block_tag})")
                return "HIT"
        
        # Handle Miss (Non Load-Through)
        self.miss_count += 1
        if len(self.cache) < self.num_blocks:
            self.cache.append({'Block': block_tag, 'Age': self.timer, 'word_address': word_address})
            self.trace_log.append(f"MISS: Word {word_address} -> Loaded Block {block_tag}")
        else:
            mru_idx = max(range(len(self.cache)), key=lambda i: self.cache[i]['Age'])
            evicted = self.cache[mru_idx]['word_address']
            self.cache[mru_idx] = {'Block': block_tag, 'Age': self.timer, 'word_address': word_address}
            self.trace_log.append(f"MISS: Word {word_address} -> Word address: {word_address} replaced word address: {evicted}")
        return "MISS"
    
        

    def calculate_metrics(self):
        hr = (self.hit_count / self.access_count * 100) if self.access_count > 0 else 0
        total_t = (self.hit_count * self.hit_time) + (self.miss_count * (self.miss_time + self.hit_time))
        amat = total_t / self.access_count if self.access_count > 0 else 0
        return {
            "Access Count": self.access_count,
            "Hits": self.hit_count, "Misses": self.miss_count,
            "Hit Rate": f"{hr:.2f}%", "Miss Rate": f"{100-hr:.2f}%",
            "AMAT": f"{amat:.2f} ns", "Total Time": f"{total_t} ns"
        }