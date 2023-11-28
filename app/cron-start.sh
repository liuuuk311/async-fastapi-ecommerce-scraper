#!/usr/bin/env bash
set -e

python3.11 web/cron_pre_start.py

python3.11 web/cron.py
