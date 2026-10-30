#!/bin/sh
# day01/index.html 후처리를 순서대로 모두 실행해요.
cd "$(dirname "$0")/.." || exit 1
export PYTHONIOENCODING=utf-8
python tools/add_day03.py && python tools/add_day04.py && python tools/add_day05.py && python tools/add_day06.py && python tools/add_day07.py && python tools/add_day08.py && python tools/add_photos2.py && python tools/add_artifacts.py && python tools/add_codes.py && python tools/restyle_day01_toc.py
