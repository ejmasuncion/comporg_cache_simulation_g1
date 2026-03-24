class MRUCacheSimulator:
    def __init__(self, words_per_block, num_blocks, hit_time, miss_time):
        self.words_per_block = words_per_block
        self.num_blocks = num_blocks
        self.hit_time = hit_time
        self.miss_time = miss_time
        
        self.cache = []
        self.timer = 0
        self.access_count = 0
        self.hit_count = 0
        self.miss_count = 0
        self.trace_log = []

        self.last_accessed_idx = -1
        self.last_result = None

    def access(self, word_address):
        self.timer += 1
        self.access_count += 1
    
        for i, entry in enumerate(self.cache):
            if entry['Word Address'] == word_address:
                entry['Age'] = self.timer
                self.hit_count += 1
                
                self.last_accessed_idx = i
                self.last_result = "HIT"
                
                self.trace_log.append(f"HIT: Word {word_address} (At Cache Block {entry['Block']})")
                return "HIT"
    
        self.miss_count += 1
        self.last_result = "MISS"
    
        if len(self.cache) < self.num_blocks:
            new_slot_index = len(self.cache)
            self.cache.append({
                'Block': new_slot_index, 
                'Word Address': word_address,
                'Age': self.timer 
            })
            self.last_accessed_idx = new_slot_index
            self.trace_log.append(f"MISS: Word {word_address} -> Loaded into Cache Block {new_slot_index}")

        else:
            mru_idx = max(range(len(self.cache)), key=lambda i: self.cache[i]['Age'])

            evicted_addr = self.cache[mru_idx]['Word Address']
            target_slot = self.cache[mru_idx]['Block'] 

            self.cache[mru_idx] = {
                'Block': target_slot, 
                'Word Address': word_address,
                'Age': self.timer
            }
            
            self.last_accessed_idx = mru_idx
            self.trace_log.append(
                f"MISS: Word {word_address} -> Word address: {word_address} replaced word address: {evicted_addr} at Block {target_slot}"
            )

        return "MISS"

    def calculate_metrics(self):
        cache_access_time = self.hit_time
        memory_access_time = self.miss_time

        # non-load through instruction
        miss_penalty = cache_access_time + self.num_blocks*memory_access_time + cache_access_time

        hr = ((self.hit_count / self.access_count) * 100) if self.access_count > 0 else 0

        total_t = (self.hit_count * self.hit_time) + (self.miss_count * (self.miss_time + self.hit_time))
        # amat = total_t / self.access_count if self.access_count > 0 else 0

        amat = (hr/100 * self.num_blocks) + (1- hr/100) * (miss_penalty)
        return {
            "Access Count": self.access_count,
            "Hits": self.hit_count, 
            "Misses": self.miss_count,
            "Hit Rate": f"{hr:.2f}%", 
            "Miss Rate": f"{100-hr:.2f}%",
            "AMAT": f"{amat:.2f} ns", 
            "Total Time": f"{total_t} ns"
        }

    def reset_results(self):
        self.cache = []
        self.timer = 0
        self.access_count = 0
        self.hit_count = 0
        self.miss_count = 0
        self.trace_log = []
        self.last_accessed_idx = -1
        self.last_result = None