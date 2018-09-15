/usr/bin/curl -L "www61.myfantasyleague.com/2018/export?TYPE=transactions&L=abcde&W=&JSON=0" > /root/mfltradebot-master/transactions.xml
/usr/bin/curl -L "www61.myfantasyleague.com/2018/export?TYPE=league&L=abcde&W=&JSON=0" > /root/mfltradebot-master/league.xml
/usr/bin/curl -L "www61.myfantasyleague.com/2018/export?TYPE=rosters&L=abcde&W=&JSON=0" >/root/mfltradebot-master/rosters.xml
/usr/bin/python [INSERT ABSOLUTE PATH TO tradebot.py HERE]
