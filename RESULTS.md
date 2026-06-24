# JSON Benchmark Lab Results

Generated: 2026-06-24T17:21:24.609395

## System Information

- **OS**: linux
- **Python**: 3.12.3
- **Platform**: Linux-6.17.0-1009-aws-x86_64-with-glibc2.39
- **Processor**: x86_64

## Tool Availability

- ✓ python_json
- ✓ jq (jq-1.7)
- ✗ simdjson
- ✓ sqlite_json1
- ✗ hyperfine
- ✓ wc
- ✓ grep

## Parse Performance

| File | Size | Tool | Mean (ms) | Min (ms) | Throughput (MB/s) | Success |
|------|------|------|-----------|----------|-------------------|---------|
| duplicate_keys.json | 0.1 KB | python_json | 0.25 | 0.23 | 0.24 | ✓ |
| duplicate_keys.json | 0.1 KB | jq | 15.69 | 15.58 | 0.00 | ✓ |
| large_array.json | 553.6 KB | python_json | 12.77 | 12.41 | 42.32 | ✓ |
| large_array.json | 553.6 KB | jq | 45.50 | 45.37 | 11.88 | ✓ |
| large_file.jsonl | 5112.1 KB | python_json | 133.38 | 132.60 | 37.43 | ✓ |
| logs.jsonl | 878.7 KB | python_json | 24.89 | 24.67 | 34.47 | ✓ |
| long_strings.json | 135.8 KB | python_json | 0.95 | 0.89 | 140.05 | ✓ |
| long_strings.json | 135.8 KB | jq | 19.62 | 19.15 | 6.76 | ✓ |
| medium_file.json | 2892.7 KB | python_json | 61.00 | 57.29 | 46.31 | ✓ |
| medium_file.json | 2892.7 KB | jq | 161.34 | 158.64 | 17.51 | ✓ |
| nested_deep.json | 389.9 KB | python_json | 2.96 | 2.85 | 128.62 | ✓ |
| nested_deep.json | 389.9 KB | jq | 29.55 | 29.00 | 12.89 | ✓ |
| nested_wide.json | 145.8 KB | python_json | 2.50 | 2.34 | 56.97 | ✓ |
| nested_wide.json | 145.8 KB | jq | 22.40 | 22.02 | 6.36 | ✓ |
| numbers.json | 0.6 KB | python_json | 0.54 | 0.46 | 1.11 | ✓ |
| numbers.json | 0.6 KB | jq | 16.36 | 16.03 | 0.04 | ✓ |
| primitives.json | 0.2 KB | python_json | 0.50 | 0.28 | 0.41 | ✓ |
| primitives.json | 0.2 KB | jq | 16.11 | 15.62 | 0.01 | ✓ |
| small_api_messages.json | 217.3 KB | python_json | 4.09 | 4.03 | 51.91 | ✓ |
| small_api_messages.json | 217.3 KB | jq | 27.07 | 26.87 | 7.84 | ✓ |
| unicode.json | 0.9 KB | python_json | 0.50 | 0.46 | 1.80 | ✓ |
| unicode.json | 0.9 KB | jq | 16.66 | 16.43 | 0.05 | ✓ |
| utf8_edge_cases.json | 0.2 KB | python_json | 0.54 | 0.49 | 0.34 | ✓ |
| utf8_edge_cases.json | 0.2 KB | jq | 16.22 | 15.83 | 0.01 | ✓ |

## Correctness Tests

### object_count

```json
{
  "test": "object_count",
  "python": 1000,
  "jq": 1000,
  "match": true
}
```

### field_extraction

```json
{
  "test": "field_extraction",
  "checksum": "52a67e4d",
  "count": 1000
}
```

### duplicate_keys

```json
{
  "test": "duplicate_keys",
  "python_result": "third",
  "note": "Python json keeps last duplicate key value"
}
```

### unicode

```json
{
  "test": "unicode",
  "emoji_count": 8,
  "sample": "\ud83d\ude00"
}
```

### number_precision

```json
{
  "test": "number_precision",
  "value": 9007199254740991,
  "type": "int"
}
```

## Notes

- All timings are mean of 3 trials
- Throughput = file size / parse time
- JSON Lines files tested with line-by-line parsing
- Invalid JSON files correctly rejected by all validators
- Duplicate keys: Python json module keeps last value (per RFC 8259, behavior is unspecified)
