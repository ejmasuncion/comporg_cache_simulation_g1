# lru.py - Fully Associative LRU with Block Mapping

class FALRUCacheSimulator:
    def __init__(self, words_per_block, num_blocks, hit_time, miss_time):
        self.words_per_block = words_per_block  # Cache Line size
        self.num_blocks = num_blocks            # Number of Cache Blocks
        self.total_mem_blocks = 1024
        
        self.hit_time = hit_time
        self.miss_time = miss_time # Penalty to fetch one full block
        
        # Cache stores: {'block_tag': ID, 'age': timestamp}
        self.cache = []
        self.timer = 0
        
        # Stats
        self.access_count = 0
        self.hit_count = 0
        self.miss_count = 0
        self.trace_log = []

    def access(self, word_address):
        self.timer += 1
        self.access_count += 1
        
        # Map word address to a Block ID (e.g., Addr 7 / 4 words per block = Block 1)
        block_tag = word_address // self.words_per_block
        
        # 1. Check for Hit
        for entry in self.cache:
            if entry['block_tag'] == block_tag:
                entry['age'] = self.timer
                self.hit_count += 1
                self.trace_log.append(f"HIT: Word {word_address} (Block {block_tag})")
                return "HIT"
        
        # 2. Handle Miss (Non Load-Through)
        self.miss_count += 1
        if len(self.cache) < self.num_blocks:
            self.cache.append({'block_tag': block_tag, 'age': self.timer})
            msg = f"MISS: Word {word_address}. Block {block_tag} loaded into empty slot."
        else:
            # LRU Eviction
            lru_idx = min(range(len(self.cache)), key=lambda i: self.cache[i]['age'])
            evicted = self.cache[lru_idx]['block_tag']
            self.cache[lru_idx] = {'block_tag': block_tag, 'age': self.timer}
            msg = f"MISS: Word {word_address}. Block {block_tag} loaded. Evicted Block {evicted}."
        
        self.trace_log.append(msg)
        return "MISS"

    def get_snapshot(self):
        if not self.cache: return "[ Cache Empty ]"
        return "\n".join([f"Block {i}: [ MemBlock Tag: {e['block_tag']} | Age: {e['age']} ]" 
                         for i, e in enumerate(self.cache)])

    def calculate_metrics(self):
        hit_rate = (self.hit_count / self.access_count) * 100 if self.access_count > 0 else 0
        miss_rate = 100 - hit_rate
        
        # Non Load-Through: Total Time = Hits*HitTime + Misses*(MissTime + HitTime)
        # Because we wait for block load (MissTime) THEN perform the read (HitTime)
        total_time = (self.hit_count * self.hit_time) + (self.miss_count * (self.miss_time + self.hit_time))
        amat = total_time / self.access_count if self.access_count > 0 else 0
        
        return {
            "1. Memory access count": self.access_count,
            "2. Cache hit count": self.hit_count,
            "3. Cache miss count": self.miss_count,
            "4. Cache hit rate": f"{hit_rate:.2f}%",
            "5. Cache miss rate": f"{miss_rate:.2f}%",
            "6. Average memory access time": f"{amat:.2f} units",
            "7. Total memory access time": f"{total_time} units"
        }