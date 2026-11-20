from app.crypto.envelope import EnvelopeCodec
from app.performance.benchmark import run_benchmark

def test_benchmark_reports_measured_values():
    report = run_benchmark(EnvelopeCodec(b"12345678", b"a" * 32), iterations=2, payload_bytes=10)
    assert report["iterations"] == 2
    assert report["encryption"]["average_ms"] > 0
    assert report["throughput_messages_per_second"] > 0
