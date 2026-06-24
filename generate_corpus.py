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

def generate_unicode_text():
    """Generate text with various Unicode characters"""
    unicode_samples = [
        "Hello 世界 🌍",
        "Café résumé naïve",
        "Emoji test: 😀🎉🚀💻",
        "Math: ∑ ∏ ∫ ∞ ≠ ≤ ≥",
        "Arabic: مرحبا",
        "Russian: Привет",
        "Japanese: こんにちは",
        "Mixed: Test™ ©® ±¼½¾",
    ]
    return random.choice(unicode_samples)

def generate_precision_boundary_numbers():
    """Generate numbers near precision boundaries"""
    return [
        9007199254740991,  # MAX_SAFE_INTEGER in JS
        9007199254740992,  # MAX_SAFE_INTEGER + 1
        -9007199254740991,
        1.7976931348623157e+308,  # Near MAX_DOUBLE
        2.2250738585072014e-308,  # Near MIN_DOUBLE
        0.1 + 0.2,  # Floating point fun
        1e-10,
        1e10,
    ]

def generate_corpus(output_dir="corpus"):
    """Generate complete test corpus"""
    ensure_dir(output_dir)
    
    print("Generating JSON benchmark corpus...")
    
    # 1. Small API messages (JSON array)
    print("  - small_api_messages.json (1000 items)")
    small_messages = [generate_small_api_message(i) for i in range(1000)]
    with open(f"{output_dir}/small_api_messages.json", "w", encoding="utf-8") as f:
        json.dump(small_messages, f, separators=(',', ':'))
    
    # 2. Large array
    print("  - large_array.json (10000 items)")
    large_array = [{"id": i, "value": random.random(), "square": i*i} for i in range(10000)]
    with open(f"{output_dir}/large_array.json", "w", encoding="utf-8") as f:
        json.dump(large_array, f, separators=(',', ':'))
    
    # 3. Nested objects
    print("  - nested_deep.json")
    nested = generate_nested_object(8, 2)
    with open(f"{output_dir}/nested_deep.json", "w", encoding="utf-8") as f:
        json.dump(nested, f, indent=2)
    
    print("  - nested_wide.json")
    wide = {f"key_{i}": generate_nested_object(3, 3) for i in range(50)}
    with open(f"{output_dir}/nested_wide.json", "w", encoding="utf-8") as f:
        json.dump(wide, f, separators=(',', ':'))
    
    # 4. JSON Lines - log-like data
    print("  - logs.jsonl (5000 lines)")
    with open(f"{output_dir}/logs.jsonl", "w", encoding="utf-8") as f:
        for i in range(5000):
            log = {
                "timestamp": f"2020-01-01T{12 + (i//3600):02d}:{(i//60)%60:02d}:{i%60:02d}Z",
                "level": random.choice(["INFO", "WARN", "ERROR", "DEBUG"]),
                "service": random.choice(["api", "worker", "db", "cache"]),
                "message": f"Request {i} processed",
                "duration_ms": random.randint(1, 5000),
                "user_id": f"u{i % 1000}",
                "tags": {"env": "prod", "version": "2.1.0"}
            }
            f.write(json.dumps(log, separators=(',', ':')) + "\n")
    
    # 5. Unicode and escaped characters
    print("  - unicode.json")
    unicode_data = {
        "unicode_samples": [generate_unicode_text() for _ in range(20)],
        "escaped": {
            "quotes": 'He said "hello" and \'goodbye\'',
            "backslashes": "C:\\Users\\Test\\file.txt",
            "newlines": "Line1\nLine2\r\nLine3\tTab",
            "unicode_escapes": "\\u0041\\u0042\\u0043",
        },
        "emoji_array": ["😀", "🎉", "🚀", "💻", "🌍", "🔥", "⭐", "💯"]
    }
    with open(f"{output_dir}/unicode.json", "w", encoding="utf-8") as f:
        json.dump(unicode_data, f, ensure_ascii=False, indent=2)
    
    # 6. Numbers and precision
    print("  - numbers.json")
    numbers_data = {
        "integers": list(range(-10, 11)),
        "big_integers": generate_precision_boundary_numbers(),
        "floats": [0.1, 0.2, 0.3, 1.0/3.0, 3.14159265359, 2.71828182846],
        "scientific": [1e10, 1e-10, 1.5e+20, 2.3e-20],
        "special": {
            "zero": 0,
            "negative_zero": -0.0,
        }
    }
    with open(f"{output_dir}/numbers.json", "w", encoding="utf-8") as f:
        json.dump(numbers_data, f, indent=2)
    
    # 7. Booleans, nulls, empty structures
    print("  - primitives.json")
    primitives = {
        "true_value": True,
        "false_value": False,
        "null_value": None,
        "empty_string": "",
        "empty_array": [],
        "empty_object": {},
        "mixed": [None, True, False, 0, "", [], {}]
    }
    with open(f"{output_dir}/primitives.json", "w", encoding="utf-8") as f:
        json.dump(primitives, f, indent=2)
    
    # 8. Long strings
    print("  - long_strings.json")
    long_text = "Lorem ipsum " * 1000
    long_strings = {
        "short": "hi",
        "medium": "x" * 1000,
        "long": long_text,
        "very_long": long_text * 10,
        "with_unicode": "Test " + "🌍" * 500
    }
    with open(f"{output_dir}/long_strings.json", "w", encoding="utf-8") as f:
        json.dump(long_strings, f, separators=(',', ':'))
    
    # 9. Duplicate keys (Note: Python's json module keeps last value)
    print("  - duplicate_keys.json")
    # We have to write this manually since json.dump would deduplicate
    with open(f"{output_dir}/duplicate_keys.json", "w", encoding="utf-8") as f:
        f.write('{"key": "first", "key": "second", "key": "third", "other": 123}')
    
    # 10. Invalid JSON files for validation testing
    print("  - invalid_*.json (various invalid formats)")
    
    invalid_cases = [
        ("invalid_trailing_comma.json", '{"a": 1, "b": 2,}'),
        ("invalid_single_quotes.json", "{'a': 1, 'b': 2}"),
        ("invalid_unquoted_keys.json", "{a: 1, b: 2}"),
        ("invalid_trailing_content.json", '{"a": 1} extra'),
        ("invalid_unclosed_array.json", "[1, 2, 3"),
        ("invalid_unclosed_object.json", '{"a": 1, "b": 2'),
        ("truncated.json", '{"test": "incomplete'),
    ]
    
    for filename, content in invalid_cases:
        with open(f"{output_dir}/{filename}", "w", encoding="utf-8") as f:
            f.write(content)
    
    # 11. Larger files for performance testing
    print("  - medium_file.json (~1MB)")
    medium_data = []
    for i in range(2000):
        medium_data.append({
            "id": i,
            "data": {
                "values": [random.random() for _ in range(20)],
                "nested": generate_nested_object(3, 2),
                "text": "x" * 100
            }
        })
    with open(f"{output_dir}/medium_file.json", "w", encoding="utf-8") as f:
        json.dump(medium_data, f, separators=(',', ':'))
    
    print("  - large_file.jsonl (~2MB)")
    with open(f"{output_dir}/large_file.jsonl", "w", encoding="utf-8") as f:
        for i in range(20000):
            record = {
                "id": i,
                "timestamp": 1609459200 + i,
                "metrics": {
                    "cpu": random.random(),
                    "memory": random.randint(1000, 16000),
                    "disk_io": random.random() * 100
                },
                "tags": [f"tag_{j}" for j in range(5)],
                "message": f"Record number {i} with some data " + "x" * 50
            }
            f.write(json.dumps(record, separators=(',', ':')) + "\n")
    
    # 12. UTF-8 edge cases
    print("  - utf8_edge_cases.json")
    utf8_cases = {
        "bom": "\ufeffTest with BOM",
        "surrogates": "Test with various unicode",
        "combining": "e\u0301 (e with acute)",  # e + combining acute
        "zero_width": "test\u200bzero\u200cwidth",
        "rtl": "Hello مرحبا שלום",
    }
    with open(f"{output_dir}/utf8_edge_cases.json", "w", encoding="utf-8") as f:
        json.dump(utf8_cases, f, ensure_ascii=False, indent=2)
    
    print(f"\nCorpus generated in '{output_dir}/'")
    print("Files created:")
    for fname in sorted(os.listdir(output_dir)):
        size = os.path.getsize(f"{output_dir}/{fname}")
        print(f"  {fname:30s} {size:>10,} bytes")

if __name__ == "__main__":
    generate_corpus()
