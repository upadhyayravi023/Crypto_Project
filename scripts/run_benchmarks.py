"""Run a repeatable local crypto benchmark and print JSON."""
import argparse
import json
from app.core.config import Settings
from app.crypto.envelope import EnvelopeCodec
from app.performance.benchmark import run_benchmark

parser = argparse.ArgumentParser()
parser.add_argument("--iterations", type=int, default=1000)
parser.add_argument("--payload-bytes", type=int, default=256)
args = parser.parse_args()
cfg = Settings.from_env()
print(json.dumps(run_benchmark(EnvelopeCodec(cfg.encryption_key, cfg.authentication_key), args.iterations, args.payload_bytes), indent=2))
