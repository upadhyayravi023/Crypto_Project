# Performance evaluation

`python -m scripts.run_benchmarks --iterations 1000 --payload-bytes 256` measures local envelope encryption and authenticated decryption. It reports observed averages, minima, maxima, standard deviations and crypto throughput. These values depend on the machine and environment; no fixed measurements are claimed. The current benchmark excludes broker and network latency, which must be measured separately in a live MQTT deployment.
