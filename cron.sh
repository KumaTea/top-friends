#!/usr/bin/env bash

set -ex

DATE=$(date +%y%m%d --date="-1 day")

# mkdir archive || :
(mkdir -p "archive/$DATE" && mv index.html "archive/$DATE/" && mv more-info.html "archive/$DATE/" && cp gen.html index.html && cp gen.html more-info.html) || :

echo "<meta http-equiv=\"refresh\" content=\"0; URL=$DATE/\" />" > "archive/index.html"

pypy3 main.py || /usr/local/bin/pypy3 main.py

mv friends.p friends_info.p "archive/$DATE/"
