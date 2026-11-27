#!/bin/bash
cd /home/claude/render
python3 -m http.server 8700 >/dev/null 2>&1 &
SP=$!
sleep 1
python3 shoot.py "$@" 2>&1 | grep -v "^ok"
kill $SP
