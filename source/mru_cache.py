# logic/lru.py

# Step through cache,  feature

class MRUCacheSimulator:
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
    
        # 1. Check for Hit
        # We look for the word_address in our existing cache lines
        for i, entry in enumerate(self.cache):
            if entry['Word Address'] == word_address:
                entry['Age'] = self.timer
                self.hit_count += 1
                # Here, entry['Block'] is already the slot index (0, 1, 2...)
                self.trace_log.append(f"HIT: Word {word_address} (At Cache Block {entry['Block']})")
                return "HIT"
    
        # 2. Handle Miss
        self.miss_count += 1
    
        # Case A: Cache has empty slots
        if len(self.cache) < self.num_blocks:
            # The new block index is simply the current length of the list
            new_slot_index = len(self.cache)
            self.cache.append({
                'Block': new_slot_index, 
                'Word Address': word_address,
                'Age': self.timer 
            })
            self.trace_log.append(f"MISS: Word {word_address} -> Loaded into Cache Block {new_slot_index}")

        # Case B: Cache is full, perform replacement (MRU logic shown here)
        else:
            # Find the index of the block with the highest Age (Most Recently Used)
            mru_idx = max(range(len(self.cache)), key=lambda i: self.cache[i]['Age'])

            evicted_addr = self.cache[mru_idx]['Word Address']
            target_slot = self.cache[mru_idx]['Block'] # Keep the same physical slot index

            # Update the entry at that specific slot
            self.cache[mru_idx] = {
                'Block': target_slot, 
                'Word Address': word_address,
                'Age': self.timer
            }

            self.trace_log.append(
                f"MISS: Word {word_address} -> Replaced Word {evicted_addr} at Cache Block {target_slot}"
            )

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

    def reset_results(self):
        self.cache = []
        self.timer = 0
        self.access_count = 0
        self.hit_count = 0
        self.miss_count = 0
        self.trace_log = []