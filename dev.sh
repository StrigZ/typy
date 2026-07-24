#!/bin/bash
find usr/lib/uncom/typy -name "*.py" -o -name "*.css" | entr -r python3 usr/lib/uncom/typy/typy.py -g