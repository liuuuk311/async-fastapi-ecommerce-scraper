#! /usr/bin/env bash
set -e

python3.11 web/worker_pre_start.py
#
python3.11 web/worker.py
