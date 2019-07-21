import xml.etree.ElementTree as ET
import os

tradeparse = ET.parse('transactions.xml')
trades = tradeparse.getroot()

leagueparse = ET.parse('league.xml')
league = leagueparse.getroot()

playerparse = ET.parse('players.xml')
players = playerparse.getroot()

rosterparse = ET.parse('rosters.xml')
rosters = rosterparse.getroot()

try:
	file = open("latest.trade", "r+")
	ltrade = file.read(10)
except:
	file = open("latest.trade", "w")
	file.close()
	ltrade = 0

def getFranchiseInfo(fnum):
	for child in league:
		if child.tag == "franchises":
			f = child
			for fchild in f:
				if fchild.attrib['id'] == fnum:
					if fchild.attrib['name'][0] == "<":
						return "Franchise " + fchild.attrib['id']
					else:
						return fchild.attrib['name'][:20]

def tradesToProcess():
	t = []
	for child in trades:
		if child.attrib['type'] == "TRADE":
			if ltrade < child.attrib['timestamp']:
				t.append(child.attrib['timestamp'])
	return t

def infoFromID(id):
	s = ""
	for child in players:
		if child.attrib['id'] == str(id):
			if child.attrib['name'] == '':
				return "An amnesty"
			s += child.attrib['team'] + " "
			s += child.attrib['position'] + " "
			s += child.attrib['name'].split(', ')[1] + " "
			s += child.attrib['name'].split(', ')[0] + " "
			s = s.replace("'","\\u0027")
			s = "".join(i for i in s if ord(i)<128)

	for child in rosters:
		for plyr in child:
			if plyr.attrib['id'] == id:
				s += "($" + plyr.attrib['salary']
				s += ", " + plyr.attrib['contractYear'] + " yrs)"

	return s

def parseGive(gave):
	print gave
	if len(gave) == 0:
		print "derp"
		return
	if gave[0] == 'D': #this years pick
		if int(gave.split('_')[2]) < 9:
			return "%s.0%s" % (str(int(gave.split('_')[1]) + 1), str(int(gave.split('_')[2]) + 1))
		else:
			return "%s.%s" % (str(int(gave.split('_')[1]) + 1), str(int(gave.split('_')[2]) + 1))
	elif gave[0] == 'F': #next years pick
		return "%s (%s) %s" % (gave.split('_')[3], gave.split('_')[2], getFranchiseInfo(gave.split('_')[1]).replace("'","\\u0027")[:16])
	else: #player
		return infoFromID(gave)


def processTrade(timestamp):
	s = "**** TRADE ALERT ****\\n"
	for child in trades:
		if child.attrib['timestamp'] == timestamp:
			f1 = child.attrib['franchise']
			f2 = child.attrib['franchise2']
			f1name = getFranchiseInfo(f1)
			f2name = getFranchiseInfo(f2)
			f1name = f1name.replace("'","\\u0027")
			f1name = "".join(i for i in f1name if ord(i)<128)
			f2name = f2name.replace("'","\\u0027")
			f2name = "".join(i for i in f2name if ord(i)<128)
			f1gave = child.attrib['franchise1_gave_up'].split(',')
			f2gave = child.attrib['franchise2_gave_up'].split(',')
			f1gave.pop()
			f2gave.pop()
			s += f1name + " gave up\\n\\n"
			for part in f1gave:
				s += str(parseGive(part)) + "\\n"
			s += "\\n" + f2name + " gave up\\n\\n"
			for part in f2gave:
				s += str(parseGive(part)) + "\\n"
			return s

GROUPME_BOTID = ""

def groupMe(s):
	cmd = "curl -d '{\"text\" : \""
	cmd += s
	cmd += "\", \"bot_id\" : \""
	cmd += GROUPME_BOTID
	cmd += "\"}'"
	cmd += " -H 'Content-Type: application/json' https://api.groupme.com/v3/bots/post"
	print cmd
	os.system(cmd)

if __name__ == '__main__':
	t = tradesToProcess()
	for tr in reversed(t):
		s = processTrade(tr)
		groupMe(s)
	if len(t) > 0:
		file.close()
		file = open("latest.trade", "w")
		print "TRADE WAS PROCESSED"
		print t[0]
		file.write(t[0])
		file.close()
	else:
		file.close()
