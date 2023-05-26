#!/bin/sh

cd /Users/jonghoon/DATA/coding/python/topsolar/

DATE=`date +%Y/%m/%d-%H:%M`

RESULT=`/opt/homebrew/bin/python3 topsolar.py`

echo $DATE $RESULT >> result.log 2>&1
