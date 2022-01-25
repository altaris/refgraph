#!/usr/bin/env bash
shopt -s globstar
python3 /app/refgraph -o "$1" "$1"/**/*.tex
