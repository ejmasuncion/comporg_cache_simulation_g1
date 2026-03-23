# source/test_cases.py
import random

class TestSequenceGenerator:
    def __init__(self, num_blocks, words_per_block):
        self.n = num_blocks
        self.wpb = words_per_block

    def get_sequential(self):
        base_sequence = list(range(2 * self.n))
        return base_sequence * 2

    def get_mid_repeat(self): 
        middle = list(range(0, self.n))
        suffix = list(range(self.n, 2 * self.n))
        
        full_cycle = middle + middle + suffix
        return full_cycle * 2

    def get_random(self):
        blocks = [random.randint(0, 2 * self.n) for _ in range(64)]
        return blocks