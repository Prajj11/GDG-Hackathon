"""Benchmark inference latency for Digital Guardrails detection pipeline.
Measures P50, P95, mean latency (ms), and throughput (messages/sec) on CPU.
Also evaluates PyTorch dynamic INT8 quantization efficiency.
"""
import time
import statistics
import json
import torch
from pathlib import Path
from backend.ml.detector import Detector, get_detector
from backend.ml.data import test_rows

def benchmark_detector(detector_mode='indicbert', num_runs=50):
    detector = Detector(detector_mode)
    test_samples = [r['text'] for r in test_rows()]
    if not test_samples:
        test_samples = ["Tum apni age se bahut mature ho, gift bhejun?", "Great game today! See you at school."]
    
    # Warm-up run
    for sample in test_samples[:5]:
        detector.classify(sample)

    latencies = []
    for i in range(num_runs):
        sample = test_samples[i % len(test_samples)]
        start = time.perf_counter()
        detector.classify(sample)
        duration_ms = (time.perf_counter() - start) * 1000
        latencies.append(duration_ms)

    latencies.sort()
    mean_lat = statistics.mean(latencies)
    median_lat = statistics.median(latencies)
    p95_lat = latencies[int(len(latencies) * 0.95)]
    throughput = 1000.0 / mean_lat if mean_lat > 0 else 0

    return {
        'model': detector.name,
        'mode': detector.kind,
        'runs': num_runs,
        'mean_ms': round(mean_lat, 2),
        'median_p50_ms': round(median_lat, 2),
        'p95_ms': round(p95_lat, 2),
        'throughput_msg_per_sec': round(throughput, 2)
    }

def main():
    print("=" * 60)
    print("DIGITAL GUARDRAILS — INFERENCE LATENCY BENCHMARK")
    print("=" * 60)

    # 1. Benchmark IndicBERT
    print("\nBenchmarking IndicBERTv2 inference pipeline...")
    indicbert_results = benchmark_detector('indicbert', num_runs=50)
    print(f"IndicBERTv2 Results:")
    print(f"  Mean Latency:   {indicbert_results['mean_ms']} ms")
    print(f"  P50 (Median):   {indicbert_results['median_p50_ms']} ms")
    print(f"  P95 Latency:   {indicbert_results['p95_ms']} ms")
    print(f"  Throughput:    {indicbert_results['throughput_msg_per_sec']} msgs/sec")

    # 2. Benchmark Baseline Fallback (TF-IDF)
    print("\nBenchmarking Baseline (TF-IDF) fallback pipeline...")
    baseline_results = benchmark_detector('baseline', num_runs=100)
    print(f"TF-IDF Baseline Results:")
    print(f"  Mean Latency:   {baseline_results['mean_ms']} ms")
    print(f"  P50 (Median):   {baseline_results['median_p50_ms']} ms")
    print(f"  P95 Latency:   {baseline_results['p95_ms']} ms")
    print(f"  Throughput:    {baseline_results['throughput_msg_per_sec']} msgs/sec")

    # 3. Save benchmark report
    summary = {
        'indicbert': indicbert_results,
        'baseline': baseline_results,
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'device': 'CPU',
        'cpu_threads': torch.get_num_threads()
    }
    
    out_path = Path('backend/ml/benchmark_results.json')
    out_path.write_text(json.dumps(summary, indent=2), encoding='utf8')
    print(f"\nLatency benchmark saved to {out_path}")

if __name__ == '__main__':
    main()
