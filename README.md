# JSON Benchmark Lab

A practical comparison of JSON parsing and querying tools, inspired by the [Hacker News discussion on simdjson](https://news.ycombinator.com/item?id=24069530) parsing gigabytes per second.

## What HN Users Were Debating

The Hacker News thread on simdjson highlighted several key tensions in JSON processing:

### 1. **"Gigabytes per second" vs Real Workloads**
- **simdjson claims**: 3+ GB/s parsing on a single core using SIMD instructions
- **Skepticism**: Small JSON messages (typical APIs) have overhead that makes "GB/s" misleading - you're often parsing 1KB documents, not streaming megabytes
- **Reality**: The flat performance line across document sizes in benchmarks suggests measurement artifacts or unrealistic test conditions

### 2. **SIMD and CPU Effects**
- Modern CPUs can process 32-64 bytes per instruction with AVX2/AVX-512
- simdjson uses vectorized classification to identify structural characters (`{`, `}`, `[`, `]`, `:`, `,`, `"`, `\`) in parallel
- Branchless algorithms matter more than raw instruction count
- Cache effects dominate for small documents; SIMD shines on large contiguous buffers

### 3. **JSON is Convenient But Not Always the Bottleneck**
- Network I/O, database queries, and business logic often dwarf parse time
- As one HN commenter noted: parsing 120KB at 3GB/s takes 0.04ms vs Python's 2ms - but does that 1.96ms difference matter in your request handler?
- "Fastest JSON parser" is meaningless without workload context

### 4. **JSON vs Binary Formats**
- Binary formats (MessagePack, CBOR, Protobuf) skip parsing entirely
- But JSON's human-readability and ubiquity create ecosystem lock-in
- Compression often negates JSON's "verbosity" disadvantage
- The performance gap narrows when you account for real-world constraints

### 5. **JSON Lines as Streamable Records**
- `.jsonl` files enable streaming processing without loading entire documents
- Critical for logs and ETL pipelines: `grep`/`wc` work because each line is independent
- Memory usage stays constant regardless of file size
- Contrasts with monolithic JSON arrays that must be fully materialized

### 6. **jq Pipelines and Practical Querying**
- jq isn't just a parser - it's a query language with filters, maps, and reductions
- Enables data exploration without writing code
- Performance characteristics differ: jq builds full AST, simdjson can use On-Demand API for partial parsing

### 7. **SQLite JSON1: Querying and Indexes**
- SQLite's JSON1 extension treats JSON as a first-class type
- `json_extract()`, `json_each()`, `json_tree()` enable SQL queries over JSON
- Can create indexes on extracted fields: `CREATE INDEX ON table(json_extract(data, '$.id'))`
- Trade-off: parsing happens at query time unless you extract to columns

### 8. **Memory Blowups from Materializing Full Trees**
- DOM parsers (Python's `json.load`, RapidJSON) build complete in-memory trees
- A 1GB JSON file can easily consume 3-5GB RAM when parsed
- Streaming parsers (SAX-style, simdjson On-Demand, JSON Lines) process incrementally
- Memory usage is often the real constraint, not CPU

### 9. **"Fastest" Depends on Workload and Correctness**
Different tools optimize for different things:

| Tool | Strength | Weakness | Best For |
|------|----------|----------|----------|
| **simdjson** | Raw parse speed, SIMD | C++ only, no mutation | Large files, data ingestion |
| **Python json** | Built-in, correct | Slow, memory-hungry | Small docs, scripting |
| **jq** | Query power, streaming | Builds AST, slower | CLI exploration, pipelines |
| **SQLite JSON1** | SQL queries, indexing | Parse-at-query-time overhead | Persistent JSON data |
| **grep/wc** | Blazing fast | Not JSON-aware | Line counting, substring search on JSONL only |

### 10. **Correctness Caveats HN Users Flagged**

- **Duplicate keys**: RFC 8259 says behavior is unspecified. Python keeps last, some parsers keep first, others error.
- **Number precision**: JSON numbers are IEEE 754 doubles. Integers > 2^53 lose precision in JavaScript. Some parsers reject out-of-range integers.
- **UTF-8 validation**: Not all parsers validate properly. Invalid sequences can be security issues.
- **Depth limits**: Deeply nested JSON can cause stack overflows. Python defaults to ~1000 levels.
- **Trailing commas, comments, single quotes**: Not valid JSON but common in the wild. Strict parsers reject them.

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

## This Benchmark

Instead of synthetic "GB/s" numbers, this lab tests realistic scenarios:

### Test Corpus
- **Small API messages**: 1000× ~500 byte objects (typical REST API)
- **Large arrays**: 10,000 element arrays
- **Nested structures**: Deep (8 levels) and wide (50 keys) objects
- **JSON Lines**: 5,000 and 20,000 line log files
- **Unicode**: Emoji, CJK, RTL text, combining characters
- **Edge cases**: Duplicate keys, precision boundaries, long strings, invalid JSON
- **Size range**: 100 bytes to ~2MB (realistic, not "parse a 10GB file")

### Operations Tested
1. **Validation**: Does it reject invalid JSON?
2. **Parsing**: Time to build in-memory representation
3. **Field extraction**: Pull specific values (simulates real usage)
4. **Filtering**: Find matching records (JSON Lines streaming)
5. **Aggregation**: Sum numeric fields
6. **Correctness**: Do all tools agree on content?

### Tools Compared
- ✅ **Python `json`** - Always available, baseline
- ⏭️ **jq** - If installed, CLI JSON processor
- ⏭️ **simdjson** - If Python bindings installed
- ⏭️ **SQLite JSON1** - If SQLite compiled with JSON1
- ✅ **wc/grep** - Only for JSON Lines line counting (NOT as JSON parsers)

Tools not installed are skipped clearly - no fake results.

## Running the Benchmark

```bash
# Generate test corpus
python3 generate_corpus.py

# Run benchmarks (3 trials per test)
python3 benchmark.py

# View results
cat RESULTS.md
```

## What the Results Mean

**Throughput (MB/s)** = File Size / Parse Time

This is NOT the same as simdjson's "GB/s" because:
- We include Python overhead, system calls, and memory allocation
- Small files (<1MB) are dominated by fixed costs
- We're measuring end-to-end time, not just SIMD kernel performance

**Correctness checks** are more important than speed:
- Do all tools parse the same number of objects?
- Are extracted fields identical (checksummed)?
- Is Unicode preserved correctly?
- How are duplicates handled?
- Do validators reject invalid JSON?

## Key Takeaways (From HN Wisdom)

1. **Measure your actual workload** - Don't optimize for GB/s if you parse 1KB API responses
2. **Memory matters more than CPU** - Can you avoid materializing the full tree?
3. **Streaming > batching** - JSON Lines often beats giant arrays
4. **Correctness over speed** - A fast parser that silently corrupts data is worthless
5. **Tool choice is contextual** - jq for exploration, simdjson for ingestion, SQLite for persistence, Python for glue code
6. **grep is not a JSON parser** - Unless you're just counting lines in JSONL, use real tools

## Files

- `generate_corpus.py` - Creates reproducible test data
- `benchmark.py` - Runs comparisons, checks correctness, generates RESULTS.md
- `corpus/` - Generated test files (gitignored, reproducible)
- `RESULTS.md` - Benchmark output with timings and system info

## Requirements

Python 3.7+ with standard library only. Optional:
- `jq` - For CLI JSON processing tests
- `pysimdjson` - `pip install pysimdjson` for simdjson tests
- SQLite 3.9+ with JSON1 extension (usually built-in)

## Honest Limitations

- This is a Python-based benchmark, so we're measuring Python's overhead too
- No C++ microbenchmarks or optimized SIMD kernels
- Results are specific to this machine and dataset
- Network, disk, and other system activity affect timings
- We test what we use in practice, not theoretical maximums

The goal isn't to crown a "fastest parser" but to understand trade-offs for real work.
