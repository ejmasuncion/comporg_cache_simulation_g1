# main.py - Configuration and Execution
import time
from source.lru_cache import FALRUCacheSimulator

def is_power_of_two(n):
    return (n & (n - 1) == 0) and n > 0

def get_input(prompt, min_val):
    while True:
        try:
            val = int(input(prompt))
            if val >= min_val and is_power_of_two(val):
                return val
            print(f"Error: Must be a power-of-2 and at least {min_val}.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def main():
    print("--- Cache Setup ---")
    words_per_block = get_input("Enter words per block (min 2): ", 2)
    num_blocks = get_input("Enter number of cache blocks (min 4): ", 4)
    
    # Timing constants for simulation
    HIT_T = 1
    MISS_T = 10  # Block transfer time
    
    sim = FALRUCacheSimulator(words_per_block, num_blocks, HIT_T, MISS_T)
    
    # Test sequence: Word addresses
    # (e.g., if words_per_block is 4, addresses 0-3 are Block 0, 4-7 are Block 1)
    sequence = [0, 1, 4, 8, 0, 12, 4, 20] 

    print("\nTracing Options: (1) Animated Trace (2) Final Snapshot")
    choice = input("Select: ")

    for addr in sequence:
        res = sim.access(addr)
        if choice == '1':
            print(f"\nAccessing Word {addr} (Block {addr//words_per_block}) -> {res}")
            print(sim.get_snapshot())
            time.sleep(0.5)

    # Final Output Requirements
    if choice != '1':
        print("\n--- a.i Final Cache Memory Snapshot ---")
        print(sim.get_snapshot())

    print("\n--- a.ii Text Log of Cache Memory Trace ---")
    print("\n".join(sim.trace_log))

    print("\n--- b. Performance Metrics ---")
    for k, v in sim.calculate_metrics().items():
        print(f"{k}: {v}")

if __name__ == "__main__":
    main()