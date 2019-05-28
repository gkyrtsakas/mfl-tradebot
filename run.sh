YEAR=2019
LEAGUE=
DIR=
##### ONLY EDIT ABOVE THIS LINE
/usr/bin/curl -L "www61.myfantasyleague.com/${YEAR}/export?TYPE=transactions&L=${LEAGUE}&W=&JSON=0" > ${DIR}/transactions.xml
/usr/bin/curl -L "www61.myfantasyleague.com/${YEAR}/export?TYPE=league&L=${LEAGUE}&W=&JSON=0" > ${DIR}/league.xml
/usr/bin/curl -L "www61.myfantasyleague.com/${YEAR}/export?TYPE=rosters&L=${LEAGUE}&W=&JSON=0" > ${DIR}/rosters.xml
/usr/bin/python ${DIR}/tradebot.py
