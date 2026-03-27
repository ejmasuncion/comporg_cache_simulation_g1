import random

class TestSequenceGenerator:
    def __init__(self, num_blocks):
        self.n = num_blocks

    def get_sequential(self):
        base_sequence = list(range(2 * self.n))
        return base_sequence * 2

    def get_mid_repeat(self): 
        middle = list(range(0, self.n))
        suffix = list(range(self.n, 2 * self.n))
        
        full_cycle = middle + middle[1:self.n] + suffix
        return full_cycle * 2

    def get_random(self):
        blocks = [random.randint(0, 1023) for _ in range(64)]
        return blocks