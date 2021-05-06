#!/usr/bin/env bash

set -e

echo "Generating date"
DATE=$(date +%y%m%d --date="-1 day")
TODAY=$(date +%y%m%d)

echo "Backing up"
mkdir archive || echo "Folder archive exists"
mkdir -p "archive/$DATE" || echo "Folder archive/$DATE exists"
mkdir -p "archive/$TODAY" || echo "Folder archive/$TODAY exists"
mv index.html more-info.html "archive/$DATE/" || echo "Already backed up"
cp gen.html index.html || echo "Already backed up"
cp gen.html more-info.html || echo "Already backed up"

echo "<meta http-equiv=\"refresh\" content=\"0; URL=$DATE/\" />" > "archive/index.html"

echo "Executing main program"
pypy3 main.py || /usr/local/bin/pypy3 main.py || /usr/local/bin/pypy3 main.py

echo "Backing up"
mv friends.p friends_info.p "archive/$TODAY/" || echo "Already backed up"
