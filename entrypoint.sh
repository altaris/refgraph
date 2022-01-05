#!/usr/bin/env bash
shopt -s globstar
python3 /app/refgraph "$1"/**/*.tex
