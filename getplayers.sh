/usr/bin/curl -L "www61.myfantasyleague.com/2018/export?TYPE=players&L=abcde&W=&JSON=0" > /root/mfltradebot-master/players.xml
a=`/bin/date`
/bin/echo "got players at $a" >> /root/cronlog
