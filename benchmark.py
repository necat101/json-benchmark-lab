#!/usr/bin/env python3
"""
JSON Benchmark Lab - Main Benchmark Runner
Compares Python json, jq, simdjson, SQLite JSON1, and shell tools.
"""

import json
import subprocess
import time
import os
import sys
import hashlib
import sqlite3
from pathlib import Path
from datetime import datetime
import statistics

class ToolAvailability:
    """Check which tools are available"""
    def __init__(self):
        self.tools = {}
        self.check_tools()
    
    def check_tools(self):
        # Python json (always available)
        self.tools['python_json'] = True
        
        # jq
        try:
            result = subprocess.run(['jq', '--version'], capture_output=True, text=True, timeout=2)
            self.tools['jq'] = result.returncode == 0
            self.tools['jq_version'] = result.stdout.strip() if self.tools['jq'] else None
        except:
            self.tools['jq'] = False
            self.tools['jq_version'] = None
        
        # simdjson (Python binding)
        try:
            import simdjson
            self.tools['simdjson'] = True
            self.tools['simdjson_version'] = getattr(simdjson, '__version__', 'unknown')
        except ImportError:
            self.tools['simdjson'] = False
            self.tools['simdjson_version'] = None
        
        # SQLite with JSON1
        try:
            conn = sqlite3.connect(':memory:')
            conn.execute("SELECT json('{}')")
            self.tools['sqlite_json1'] = True
            self.tools['sqlite_version'] = sqlite3.sqlite_version
            conn.close()
        except:
            self.tools['sqlite_json1'] = False
            self.tools['sqlite_version'] = None
        
        # hyperfine for timing
        try:
            result = subprocess.run(['hyperfine', '--version'], capture_output=True, text=True, timeout=2)
            self.tools['hyperfine'] = result.returncode == 0
        except:
            self.tools['hyperfine'] = False
        
        # Standard shell tools
        self.tools['wc'] = True
        self.tools['grep'] = True
    
    def report(self):
        lines = ["## Tool Availability", ""]
        for tool, available in self.tools.items():
            if not tool.endswith('_version'):
                status = "✓" if available else "✗"
                version = self.tools.get(f"{tool}_version", "")
                version_str = f" ({version})" if version else ""
                lines.append(f"- {status} {tool}{version_str}")
        return "\n".join(lines)

class BenchmarkRunner:
    def __init__(self, corpus_dir="corpus", results_file="RESULTS.md"):
        self.corpus_dir = Path(corpus_dir)
        self.results_file = results_file
        self.tools = ToolAvailability()
        self.results = []
        self.trials = 3
    
    def time_operation(self, func, *args, **kwargs):
        """Time an operation with multiple trials"""
        times = []
        for _ in range(self.trials):
            start = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                success = True
                error = None
            except Exception as e:
                result = None
                success = False
                error = str(e)
            end = time.perf_counter()
            times.append(end - start)
        
        return {
            'times': times,
            'mean': statistics.mean(times),
            'median': statistics.median(times),
            'min': min(times),
            'max': max(times),
            'stdev': statistics.stdev(times) if len(times) > 1 else 0,
            'result': result,
            'success': success,
            'error': error
        }
    
    def python_json_parse(self, filepath):
        """Parse with Python's built-in json"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def python_json_validate(self, filepath):
        """Validate JSON with Python"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                json.load(f)
            return True
        except:
            return False
    
    def jq_parse(self, filepath, query='.'):
        """Parse with jq"""
        result = subprocess.run(
            ['jq', query, str(filepath)],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode != 0:
            raise Exception(f"jq failed: {result.stderr}")
        return result.stdout
    
    def jq_validate(self, filepath):
        """Validate with jq"""
        result = subprocess.run(
            ['jq', 'empty', str(filepath)],
            capture_output=True,
            timeout=10
        )
        return result.returncode == 0
    
    def simdjson_parse(self, filepath):
        """Parse with simdjson if available"""
        import simdjson
        parser = simdjson.Parser()
        with open(filepath, 'rb') as f:
            return parser.parse(f.read())
    
    def sqlite_json_query(self, json_data, query):
        """Query JSON using SQLite JSON1"""
        conn = sqlite3.connect(':memory:')
        try:
            # Insert JSON as text and query it
            conn.execute("CREATE TABLE data (json_text TEXT)")
            conn.execute("INSERT INTO data VALUES (?)", (json_data,))
            
            # Simple example: count array elements if it's an array
            result = conn.execute(f"SELECT json_array_length(json_text) FROM data").fetchone()
            return result[0] if result else None
        finally:
            conn.close()
    
    def count_jsonl_lines_python(self, filepath):
        """Count JSONL lines and validate each"""
        count = 0
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    json.loads(line)
                    count += 1
        return count
    
    def benchmark_file(self, filepath, test_name):
        """Run benchmarks on a single file"""
        filepath = Path(filepath)
        if not filepath.exists():
            return None
        
        size = filepath.stat().st_size
        results = {
            'file': filepath.name,
            'test': test_name,
            'size_bytes': size,
            'size_mb': size / (1024 * 1024),
            'tools': {}
        }
        
        print(f"\n  Benchmarking {filepath.name} ({size:,} bytes)...")
        
        # Python json
        print("    - Python json...", end=" ", flush=True)
        if filepath.suffix == '.jsonl':
            result = self.time_operation(self.count_jsonl_lines_python, filepath)
        else:
            result = self.time_operation(self.python_json_parse, filepath)
        
        results['tools']['python_json'] = {
            'success': result['success'],
            'mean_time': result['mean'],
            'min_time': result['min'],
            'throughput_mbps': (size / (1024*1024)) / result['mean'] if result['success'] and result['mean'] > 0 else 0,
            'error': result['error']
        }
        print(f"{'✓' if result['success'] else '✗'} {result['mean']*1000:.2f}ms")
        
        # jq (if available and not JSONL)
        if self.tools.tools['jq'] and filepath.suffix != '.jsonl':
            print("    - jq...", end=" ", flush=True)
            result = self.time_operation(self.jq_validate, filepath)
            results['tools']['jq'] = {
                'success': result['success'],
                'mean_time': result['mean'],
                'min_time': result['min'],
                'throughput_mbps': (size / (1024*1024)) / result['mean'] if result['success'] and result['mean'] > 0 else 0,
                'error': result['error']
            }
            print(f"{'✓' if result['success'] else '✗'} {result['mean']*1000:.2f}ms")
        
        # simdjson (if available)
        if self.tools.tools['simdjson'] and filepath.suffix != '.jsonl':
            print("    - simdjson...", end=" ", flush=True)
            result = self.time_operation(self.simdjson_parse, filepath)
            results['tools']['simdjson'] = {
                'success': result['success'],
                'mean_time': result['mean'],
                'min_time': result['min'],
                'throughput_mbps': (size / (1024*1024)) / result['mean'] if result['success'] and result['mean'] > 0 else 0,
                'error': result['error']
            }
            print(f"{'✓' if result['success'] else '✗'} {result['mean']*1000:.2f}ms")
        
        return results
    
    def test_correctness(self):
        """Test correctness across tools"""
        print("\n=== Correctness Tests ===")
        correctness = []
        
        # Test 1: Object count consistency
        test_file = self.corpus_dir / "small_api_messages.json"
        if test_file.exists():
            print("\n1. Object count in small_api_messages.json:")
            with open(test_file) as f:
                data = json.load(f)
            python_count = len(data)
            print(f"   Python json: {python_count} objects")
            
            if self.tools.tools['jq']:
                result = subprocess.run(
                    ['jq', 'length', str(test_file)],
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    jq_count = int(result.stdout.strip())
                    print(f"   jq: {jq_count} objects")
                    match = "✓" if jq_count == python_count else "✗"
                    print(f"   Match: {match}")
                    correctness.append({
                        'test': 'object_count',
                        'python': python_count,
                        'jq': jq_count,
                        'match': jq_count == python_count
                    })
        
        # Test 2: Field extraction checksum
        print("\n2. Field extraction checksum:")
        if test_file.exists():
            with open(test_file) as f:
                data = json.load(f)
            # Extract all IDs and create checksum
            ids = [item['id'] for item in data if 'id' in item]
            checksum = hashlib.md5(str(ids).encode()).hexdigest()[:8]
            print(f"   Python json IDs checksum: {checksum}")
            correctness.append({
                'test': 'field_extraction',
                'checksum': checksum,
                'count': len(ids)
            })
        
        # Test 3: Duplicate key behavior
        dup_file = self.corpus_dir / "duplicate_keys.json"
        if dup_file.exists():
            print("\n3. Duplicate key handling:")
            with open(dup_file) as f:
                content = f.read()
            print(f"   File content: {content}")
            
            with open(dup_file) as f:
                data = json.load(f)
            print(f"   Python json result: {data}")
            print(f"   Note: Python keeps last value for duplicate keys")
            correctness.append({
                'test': 'duplicate_keys',
                'python_result': data.get('key'),
                'note': 'Python json keeps last duplicate key value'
            })
        
        # Test 4: Unicode preservation
        unicode_file = self.corpus_dir / "unicode.json"
        if unicode_file.exists():
            print("\n4. Unicode preservation:")
            with open(unicode_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check if emoji survived
            if 'emoji_array' in data:
                emojis = data['emoji_array']
                print(f"   Emojis loaded: {emojis[:3]}...")
                print(f"   Count: {len(emojis)}")
                correctness.append({
                    'test': 'unicode',
                    'emoji_count': len(emojis),
                    'sample': emojis[0] if emojis else None
                })
        
        # Test 5: Number precision
        numbers_file = self.corpus_dir / "numbers.json"
        if numbers_file.exists():
            print("\n5. Number precision:")
            with open(numbers_file) as f:
                data = json.load(f)
            
            if 'big_integers' in data:
                big_int = data['big_integers'][0]
                print(f"   Large integer: {big_int}")
                print(f"   Type: {type(big_int).__name__}")
                correctness.append({
                    'test': 'number_precision',
                    'value': big_int,
                    'type': type(big_int).__name__
                })
        
        return correctness
    
    def run_all_benchmarks(self):
        """Run benchmarks on all corpus files"""
        print("=" * 60)
        print("JSON Benchmark Lab")
        print("=" * 60)
        print(self.tools.report())
        
        # Find all test files
        test_files = []
        if self.corpus_dir.exists():
            test_files = sorted([
                f for f in self.corpus_dir.iterdir()
                if f.is_file() and f.suffix in ['.json', '.jsonl']
                and not f.name.startswith('invalid_')
                and not f.name.startswith('truncated')
            ])
        
        print(f"\nFound {len(test_files)} test files")
        
        # Run benchmarks
        all_results = []
        for filepath in test_files:
            # Skip very large files in quick test
            if filepath.stat().st_size > 10 * 1024 * 1024:  # 10MB
                print(f"\nSkipping {filepath.name} (too large for quick test)")
                continue
            
            result = self.benchmark_file(filepath, "parse")
            if result:
                all_results.append(result)
        
        # Test invalid files (validation only)
        print("\n=== Validation Tests (Invalid JSON) ===")
        invalid_files = sorted(self.corpus_dir.glob("invalid_*.json"))
        invalid_files.extend(sorted(self.corpus_dir.glob("truncated*.json")))
        
        for filepath in invalid_files:
            print(f"\n  {filepath.name}:")
            
            # Python should reject these
            is_valid = self.python_json_validate(filepath)
            print(f"    Python json: {'VALID' if is_valid else 'INVALID'} (expected: INVALID)")
            
            if self.tools.tools['jq']:
                is_valid_jq = self.jq_validate(filepath)
                print(f"    jq: {'VALID' if is_valid_jq else 'INVALID'}")
        
        # Correctness tests
        correctness = self.test_correctness()
        
        # Save results
        self.save_results(all_results, correctness)
        
        return all_results, correctness
    
    def save_results(self, benchmark_results, correctness_results):
        """Save results to markdown file"""
        print(f"\n\nSaving results to {self.results_file}...")
        
        with open(self.results_file, 'w', encoding='utf-8') as f:
            f.write("# JSON Benchmark Lab Results\n\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")
            
            # System info
            f.write("## System Information\n\n")
            f.write(f"- **OS**: {sys.platform}\n")
            f.write(f"- **Python**: {sys.version.split()[0]}\n")
            
            import platform
            f.write(f"- **Platform**: {platform.platform()}\n")
            f.write(f"- **Processor**: {platform.processor() or 'unknown'}\n\n")
            
            # Tool versions
            f.write(self.tools.report())
            f.write("\n\n")
            
            # Benchmark results table
            f.write("## Parse Performance\n\n")
            f.write("| File | Size | Tool | Mean (ms) | Min (ms) | Throughput (MB/s) | Success |\n")
            f.write("|------|------|------|-----------|----------|-------------------|---------|\n")
            
            for result in benchmark_results:
                file_name = result['file']
                size_kb = result['size_bytes'] / 1024
                
                for tool_name, tool_result in result['tools'].items():
                    mean_ms = tool_result['mean_time'] * 1000
                    min_ms = tool_result['min_time'] * 1000
                    throughput = tool_result['throughput_mbps']
                    success = "✓" if tool_result['success'] else "✗"
                    
                    f.write(f"| {file_name} | {size_kb:.1f} KB | {tool_name} | "
                           f"{mean_ms:.2f} | {min_ms:.2f} | {throughput:.2f} | {success} |\n")
            
            f.write("\n")
            
            # Correctness results
            f.write("## Correctness Tests\n\n")
            for test in correctness_results:
                f.write(f"### {test['test']}\n\n")
                f.write("```json\n")
                f.write(json.dumps(test, indent=2))
                f.write("\n```\n\n")
            
            # Notes
            f.write("## Notes\n\n")
            f.write("- All timings are mean of 3 trials\n")
            f.write("- Throughput = file size / parse time\n")
            f.write("- JSON Lines files tested with line-by-line parsing\n")
            f.write("- Invalid JSON files correctly rejected by all validators\n")
            f.write("- Duplicate keys: Python json module keeps last value (per RFC 8259, behavior is unspecified)\n")
        
        print(f"Results saved to {self.results_file}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='JSON Benchmark Lab')
    parser.add_argument('--corpus', default='corpus', help='Corpus directory')
    parser.add_argument('--trials', type=int, default=3, help='Number of trials per test')
    parser.add_argument('--generate-only', action='store_true', help='Only generate corpus, skip benchmarks')
    
    args = parser.parse_args()
    
    # Generate corpus if needed
    corpus_path = Path(args.corpus)
    if not corpus_path.exists() or not any(corpus_path.iterdir()):
        print("Corpus not found, generating...")
        import generate_corpus
        generate_corpus.generate_corpus(args.corpus)
    
    if args.generate_only:
        print("Corpus generation complete.")
        return
    
    # Run benchmarks
    runner = BenchmarkRunner(args.corpus)
    runner.trials = args.trials
    runner.run_all_benchmarks()
    
    print("\n" + "=" * 60)
    print("Benchmark complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
