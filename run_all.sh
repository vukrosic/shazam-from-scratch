#!/bin/sh
# Every step runs on a laptop CPU in under a minute. Nothing is downloaded and nothing is trained.
set -e
cd "$(dirname "$0")"
mkdir -p files
python step1_samples.py
python step2_compare.py
python step3_frequencies.py
python step4_peaks.py
python step5_hashes.py
python step6_match.py
python step7_test.py
python solution.py
python tests.py
