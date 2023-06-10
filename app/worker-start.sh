#! /usr/bin/env bash
set -e

python web/worker_pre_start.py

python web/worker.py