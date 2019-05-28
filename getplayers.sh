YEAR=2019
LEAGUE=
DIR=
#### ONLY EDIT ABOVE THIS LINE
/usr/bin/curl -L "www61.myfantasyleague.com/${YEAR}/export?TYPE=players&L=${LEAGUE}&W=&JSON=0" > ${DIR}/players.xml
#a=`/bin/date`
#/bin/echo "got players at $a" >> /root/cronlog
