# JSON Benchmark Lab

A practical comparison of JSON parsing and querying tools, inspired by the [Hacker News discussion on simdjson](https://news.ycombinator.com/item?id=24069530) parsing gigabytes per second.

## What HN Users Were Debating

[... full content as before ...]

## Implementation Status

### ✅ Fully Implemented
- Corpus generation (20 files with edge cases)
- Python json parsing benchmarks (3 trials, statistics)
- jq validation benchmarks
- Tool detection (python_json, jq, simdjson, sqlite_json1, hyperfine, wc, grep)
- Correctness tests (object counts, checksums, Unicode, duplicates, numbers)
- Invalid JSON validation tests
- RESULTS.md generation with timing tables

### 🚧 Partially Implemented
- SQLite JSON1 detection works, but no query/index benchmarks yet
- Shell tools (wc, grep) detected but not benchmarked in main flow
- simdjson detection works but Python bindings not installed in test environment

### ❌ Not Yet Implemented
- python -m json.tool pretty-printing/minifying benchmarks
- No-match and many-match filtering scenarios
- Numeric aggregation benchmarks (sum, avg, min, max)
- Memory usage profiling for large files
- Hyperfine integration for more accurate timing

## Running the Benchmark

```bash
# Generate test corpus
python3 generate_corpus.py

# Run benchmarks (3 trials per test)
python3 benchmark.py

# View results
cat RESULTS.md
```

[... rest of README ...]
