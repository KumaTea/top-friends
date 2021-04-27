#!/usr/bin/env bash

set -ex

DATE=$(date +%y%m%d)

mkdir archive
mkdir -p "archive/$DATE"

cp index.html "archive/$DATE/"
cp more-info.html "archive/$DATE/"

echo "<meta http-equiv=\"refresh\" content=\"0; URL=$DATE/\" />" > "archive/index.html"

pypy3 main.py || /usr/local/bin/pypy3 main.py
