#!/usr/bin/env python3
"""
JSON Benchmark Lab - Corpus Generator
Generates reproducible JSON and JSONL test files covering edge cases.
"""

import json
import random
import string
import os
from pathlib import Path

def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)

def generate_small_api_message(i):
    """Small API-like message"""
    return {
        "id": i,
        "type": "event",
        "timestamp": 1609459200 + i,
        "user": {
            "id": f"user_{i % 1000}",
            "name": f"User {i}"
        },
        "data": {
            "action": random.choice(["click", "view", "purchase"]),
            "value": random.random() * 1000,
            "metadata": {
                "source": "web",
                "version": "1.0.0"
            }
        },
        "tags": ["api", "test", f"batch_{i // 100}"]
    }

def generate_nested_object(depth, width=3):
    """Generate deeply nested object"""
    if depth <= 0:
        return {
            "value": random.randint(0, 1000000),
            "text": "leaf_" + ''.join(random.choices(string.ascii_letters, k=10))
        }
    
    obj = {}
    for i in range(width):
        key = f"level_{depth}_item_{i}"
        if random.random() < 0.3 and depth > 1:
            obj[key] = [generate_nested_object(depth - 1, width) for _ in range(2)]
        else:
            obj[key] = generate_nested_object(depth - 1, width)
    return obj

def generate_corpus(output_dir="corpus"):
    """Generate complete test corpus"""
    ensure_dir(output_dir)
    print("Generating JSON benchmark corpus...")
    
    # Small API messages
    small_messages = [generate_small_api_message(i) for i in range(1000)]
    with open(f"{output_dir}/small_api_messages.json", "w") as f:
        json.dump(small_messages, f, separators=(',', ':'))
    
    # Large array
    large_array = [{"id": i, "value": random.random(), "square": i*i} for i in range(10000)]
    with open(f"{output_dir}/large_array.json", "w") as f:
        json.dump(large_array, f, separators=(',', ':'))
    
    # Nested objects
    nested = generate_nested_object(8, 2)
    with open(f"{output_dir}/nested_deep.json", "w") as f:
        json.dump(nested, f, indent=2)
    
    print(f"Corpus generated in '{output_dir}/'")

if __name__ == "__main__":
    generate_corpus()
