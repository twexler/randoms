#!/usr/bin/python
#Author: Ted Wexler
#Date: 5/11/2011
#idea, html substring code, strip_tags, replace_space, and scoreboard formatting credit bhaviksblog.com
#License: GNU GPL v3.0
#License URL: http://www.gnu.org/licenses/gpl.html
#Requires BeautifulSoup - http://www.crummy.com/software/BeautifulSoup/
from BeautifulSoup import BeautifulSoup
import urllib2, sys, re

def main(argv):
	team = ""
	try:
		team = argv[0]
	except:
		pass
	if len(argv) > 1:
		if "last" in argv: last = True
	else: last = False
	if not team: team = "sharks"
	page = urllib2.urlopen('http://%s.nhl.com/index.html' % (team))
	if not page: 
		print "something bad happened"
		sys.exit(1)
	html = ''.join(page.readlines())
	# pos finds our start flag. Lets hope the NHL will stick to this layout
	if last:
		pos = html.find('<div id="lastGameBody">')
	        rpos = html.find('</div><!-- end lastGameBody')
	        substring = html[pos:rpos] #extract info between flags
        	soup = BeautifulSoup(substring)
	        try:
        	        gamebox = soup.findAll(id='lastGameBody')[0]
        	except:
                	#no future game...
                	print "No last game"
	else:
		pos = html.find('<div id="nextGameBody">')

		# rpos finds the end flag. The scoreboard is between the flags
		rpos = html.find('</div><!-- end nextGameBody')
		substring = html[pos:rpos] #extract info between flags
		soup = BeautifulSoup(substring)
		try:
			gamebox = soup.findAll(id='nextGameBody')[0]
		except:
			#no future game...
			print "No Games Scheduled!"
			sys.exit(0)
	
	status = remove_space(gamebox.findAll(attrs={'class': 'status'})[0].string)
	if 'PROGRESS' in status or "FINAL" in status:
		#game is in progress, get score etc
		scorebox = getObjectByClassName(gamebox, 'score')
		teambox1 = scorebox[0]
		teambox2 = scorebox[1]
		team1 = getObjectByClassName(teambox1,'team')[0].string
		team2 = getObjectByClassName(teambox2,'team')[0].string
		team1_tot = getObjectByClassName(teambox1,'goals_tot')[0].string
		team2_tot = getObjectByClassName(teambox2,'goals_tot')[0].string
		team1_goals = parseGoals(teambox1)
		team2_goals = parseGoals(teambox2)
		print ''
		print '%12s' % 'Teams','%5s' % '1st','%5s' % '2nd','%5s' % '3rd','%6s' % 'Total'
                print '---------------------------------------'
		print '%12s' % team1,'%5s' % team1_goals['1'],'%5s' % team1_goals['2'],'%5s' % team1_goals['3'],'%6s' % team1_tot
		print '%12s' % team2,'%5s' % team2_goals['1'],'%5s' % team2_goals['2'],'%5s' % team2_goals['3'],'%6s' % team2_tot
		print ''
	else:
		#future game
		datescorebox = getObjectByClassName(gamebox,'cgdDateScore')[0]
		datebox = datescorebox.findAll('span')[0]
		date = remove_space(datebox.findAll(True)[1].string)
		time = remove_space(datebox.findAll(True)[2].string)
		tv = remove_space(getObjectByClassName(gamebox,'cgdTvRadioInfo')[0].contents[2])
		radio = strip_tags(getObjectByClassName(gamebox,'cgdTvRadioInfo')[0].contents[5].string)
		if radio == "Listen": radio = "None"
		print "Next Game:\t\t%s\t%s\nLIVE ON:\t\t%s\nRADIO:\t\t\t%s" % (date,time,tv,radio)

# Strips more than one consecutive space
def remove_space(value):
    temp = re.compile(r'\s+')
    return temp.sub(' ', value)[1:] #there always seems to be an extra bit of whitespace here..

#strips html tags
def strip_tags(value):
    return re.sub(r'<[^>]*?>', '', value)

#get a BeautifulSoup object by class name
def getObjectByClassName(origobj, name):
	return origobj.findAll(attrs={'class': name})

#parse out the goal info from a team box
def parseGoals(teambox):
	team_goals = {}
	i = 1
	for goalbox in getObjectByClassName(teambox,'goals'):
		if goalbox.string == "&nbsp;": num = 0
		else: num = goalbox.string
		team_goals[str(i)] = str(num)
		i += 1
	return team_goals

if __name__ == '__main__':
    main(sys.argv[1:])
