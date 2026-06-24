#!/usr/bin/env python3
"""
JSON Benchmark Lab - Main Benchmark Runner
Compares Python json, jq, and other available tools.
"""

import json
import subprocess
import time
from pathlib import Path

def benchmark_file(filepath):
    """Benchmark a single JSON file"""
    with open(filepath, 'r') as f:
        start = time.perf_counter()
        data = json.load(f)
        elapsed = time.perf_counter() - start
    return elapsed, len(str(data))

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        elapsed, size = benchmark_file(filepath)
        print(f"Parsed {filepath} in {elapsed*1000:.2f}ms")
    else:
        print("Usage: python3 benchmark.py <file.json>")
        print("For full benchmark suite, see README.md")
