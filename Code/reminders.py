from common import *
from fileIO import load
import datetime
from timeParsing import *
from memory import *
from graphics import *


def timeDiff(T1, T2=[], short=False):
	# [TD["year"], TD["month"],TD["day"],TD["hour"],TD["minute"],TD["second"]]


	T2p = []
	if T2 == []:
		T2 = getTimeVec("now")
	
	T2p = datetime.datetime(year = T2['year'], month=T2['month'], day=T2['day'], hour=T2['hour'], minute=T2['minute'], second=T2['second'])
	T1p = datetime.datetime(year = T1['year'], month=T1['month'], day=T1['day'], hour=T1['hour'], minute=T1['minute'], second=T1['second'])

	T1TotalSecs = (T1p-datetime.datetime(1970,1,1)).total_seconds()
	T2TotalSecs = (T2p-datetime.datetime(1970,1,1)).total_seconds()

	T1InFuture = (T1TotalSecs > T2TotalSecs)

	#print "T1:", T1

	#if T1InFuture:
	#	print "T1 in future"

	tDiff = 0
	if T1InFuture:
		tDiff = T1TotalSecs - T2TotalSecs
	else:
		tDiff = T2TotalSecs - T1TotalSecs

	daysDiff = math.floor(tDiff/(86400.0))
	tDiff = tDiff - 86400.0*daysDiff

	hoursDiff = math.floor(tDiff/(3600.0))
	tDiff = tDiff - 3600.0*hoursDiff

	minutesDiff = math.floor(tDiff/(60.0))
	tDiff = tDiff - 60.0*minutesDiff

	secondsDiff = tDiff#math.floor(tDiff/(60))
	#tDiff = tDiff - 60.0*hoursDiff

	#print daysDiff, "days"
	#print hoursDiff, "hours"
	#print minutesDiff, "minutes"
	#print secondsDiff, "seconds"

	# combine values into str

	diffStr=""

	if short:
		numStr=0
		if daysDiff != 0:
			if numStr < 2:
				diffStr += (' %s'%int(daysDiff))+"d"
				numStr += 1
		if hoursDiff != 0:
			if numStr < 2:
				diffStr += (' %s'%int(hoursDiff))+"h"
				numStr += 1
		if minutesDiff != 0:
			if numStr < 2:
				diffStr += (' %s'%int(minutesDiff))+"m"
				numStr += 1
		if secondsDiff != 0:
			if numStr < 2:
				diffStr += (' %s'%int(secondsDiff))+"s"
				numStr += 1
	else:

		if daysDiff != 0:
			if daysDiff == 1:
				diffStr += (' %s'%int(daysDiff))+" day"
			else:
				diffStr += (' %s'%int(daysDiff))+" days"
		if hoursDiff != 0:
			if hoursDiff == 1:
				diffStr += (' %s'%int(hoursDiff))+" hour"
			else:
				diffStr += (' %s'%int(hoursDiff))+" hours"
		if minutesDiff != 0:
			if minutesDiff == 1:
				diffStr += (' %s'%int(minutesDiff))+" minute"
			else:
				diffStr += (' %s'%int(minutesDiff))+" minutes"
		if secondsDiff != 0:
			if secondsDiff == 1:
				diffStr += (' %s'%int(secondsDiff))+" second"
			else:
				diffStr += (' %s'%int(secondsDiff))+" seconds"

	if T1InFuture:
		if short:
			diffStr = "-"+diffStr
		else:
			diffStr = "in"+diffStr
	else:
		if short:
			diffStr = "+"+diffStr
		else:
			diffStr = diffStr+" ago"

	#print "DIFFSTR:", diffStr.strip()

	return diffStr.strip()


def toDict(T):
	# [TD["year"], TD["month"],TD["day"],TD["hour"],TD["minute"],TD["second"]]


	TD = {"year":T[0], "month":T[1], "day":T[2], "hour":T[3], "minute":T[4], "second":T[5]}


	return TD


def secondsDiff(T1, T2):
	T2p = datetime.datetime(year = T2['year'], month=T2['month'], day=T2['day'], hour=T2['hour'], minute=T2['minute'], second=T2['second'])
	T1p = datetime.datetime(year = T1['year'], month=T1['month'], day=T1['day'], hour=T1['hour'], minute=T1['minute'], second=T1['second'])

	T1TotalSecs = (T1p-datetime.datetime(1970,1,1)).total_seconds()
	T2TotalSecs = (T2p-datetime.datetime(1970,1,1)).total_seconds()

	return T1TotalSecs - T2TotalSecs

def sendText(inStr):
	# TODO: replace the placeholder phone number with your own
	return

	inStr = inStr.replace('\'', '')
	inStr = inStr.replace('\"', '')
	cmdStr="""curl http://textbelt.com/canada -d number=5555555555 -d "message="""+inStr+"\""" > /dev/null 2>&1 &"

	#print "CMD:", cmdStr

	#cmdStr=setting("WEB_BROWSER")+" https://www.youtube.com/results?search_query="+matches[0][0].replace(' ','+')+" > /dev/null 2>&1 &"
	subprocess.call(cmdStr, shell=True)

# IN CMDS
def reminders(inCmd, inStr, matches=[[],[]]):
	from determineFunction import refineMatches, findCMD
	from Fermi import substituteBiographicMemory
	from timeParsing import getTimeVec

	#print "HERE"

	matches = refineMatches(inCmd, inStr)

	matches = substituteBiographicMemory(matches, queryType='what is', append=True, maxContextSub=5)

	inStr = inStr.lower()


	if len(matches[1]) == 0:
		matches[1].append("add") # default mode

	#print "MATCHES:", matches

		
	mode=""
	
	if "add" in matches[1]:
		mode="add"
	elif "list" in matches[1]:
		mode="list"
	elif "check" in matches[1] or "check off" in matches[1]:
		mode="check"
	elif "uncheck" in matches[1]:
		mode="uncheck"
	elif "delete" in matches[1] or "remove" in matches[1]:
		mode="delete"
	elif "purge" in inStr:
		mode="purge"
	elif len(matches[0]) > 0:
		mode = "add"
	else:
		say(getResponse(findCMD("rephrase")), more=False, speak=setting("SPEAK"), moodUpdate=True)
		return False

	#print "MODE:", mode
	
	

	REMINDERS=load(DATA_DIR+"reminders.txt", LPC=1)
	REMINDERS=[s[0] for s in REMINDERS]

	#print REMINDERS

	#return True

	updateReminders = False
	
	
	if mode=="add":
		# see if you need to ask for the reminder to add
		#if newStr.split() == [] or k.cleanWord(newStr)=='':
		if len(matches[0]) == 0:
			

			#say("What reminder would you like to add?", more=True, speak=setting("SPEAK"), moodUpdate=True)

			newStr=questionBox("What reminder would you like to add?")
			
			#newStr = raw_input("")
			


			if newStr == "xx":
				return True
			else:
				matches[0].append(newStr)

		# look for a time tag
		if "@+" in matches[0][0]:
			matches[0].append(matches[0][0][matches[0][0].index("@+")+2:])
			matches[0][0] = matches[0][0][:matches[0][0].index("@+")]
			matches[0][0] = matches[0][0].strip()
			matches[0][1] = matches[0][1].strip()

		TD=[]
		if len(matches[0]) == 1:
			# see if it has a time tag
			timeNow = getTimeVec("now")
			if "@-" in matches[0][0]: # prevent any time tags
				TD = timeNow
				matches[0][0] = matches[0][0].replace("@-", "").strip()
			else:
				TD = getTimeVec(matches[0][0])
			timeVec=[TD["year"], TD["month"],TD["day"],TD["hour"],TD["minute"],TD["second"]]
		else:
			# time tag said after @
			#print "TIME TAG:", matches[0][1]
			timeNow = getTimeVec("now")
			TD = getTimeVec(matches[0][1])
			timeVec=[TD["year"], TD["month"],TD["day"],TD["hour"],TD["minute"],TD["second"]]

		rStr = processResponse(getResponse(inCmd), ["Adding", matches[0][0]])
		say(rStr, more=False, speak=setting("SPEAK"))

		if abs(secondsDiff(timeNow, TD)) >= 10:
			rStr = "I will remind you "+timeDiff(TD)+"."
			say(rStr, more=False, speak=setting("SPEAK"))
		else:
			timeVec = []

		# message, time tag, been reminded
		REMINDERS.append((matches[0][0], timeVec, False))
		updateReminders = True

	if mode=="check":
		# see if you need to ask for the reminder to check off
		if len(matches[0]) == 0:
			#say("What reminder would you like to check off?", more=True, speak=setting("SPEAK"), moodUpdate=True)
			#newStr = raw_input("")
			newStr=questionBox("What reminder would you like to check off?")
			if newStr == "xx":
				return True
			else:
				matches[0].append(newStr)

		maxMatch=0 # calculate nearest reminder
		topLine=0 # save index of line to delete

		for i in range(len(REMINDERS)):
			matchScore = wordSim(REMINDERS[i][0], matches[0][0])
			if matchScore >= maxMatch:
				maxMatch = matchScore
				topLine=i

		rStr=processResponse("Are you sure you would like to check off: #0#?", [REMINDERS[topLine][0]])
		#say(rStr, more=True, speak=setting("SPEAK"), moodUpdate=True)
		#YN=raw_input("")
		#if getYesNo(YN):
		YN = yesNoBox(rStr)
		if YN:
			# remove reminders
			REMINDERS[topLine] = (REMINDERS[topLine][0], REMINDERS[i][1], True)
			say("Note checked off!", more=False, speak=setting("SPEAK"), moodUpdate=True)
			updateReminders = True

	if mode=="uncheck":
		# see if you need to ask for the reminder to check off
		if len(matches[0]) == 0:
			#say("What reminder would you like to uncheck?", more=True, speak=setting("SPEAK"), moodUpdate=True)
			#newStr = raw_input("")
			newStr=questionBox("What reminder would you like to uncheck?")
			if newStr == "xx":
				return True
			else:
				matches[0].append(newStr)

		maxMatch=0 # calculate nearest reminder
		topLine=0 # save index of line to delete

		for i in range(len(REMINDERS)):
			matchScore = wordSim(REMINDERS[i][0], matches[0][0])
			if matchScore >= maxMatch:
				maxMatch = matchScore
				topLine=i

		rStr=processResponse("Are you sure you would like to uncheck: #0#?", [REMINDERS[topLine][0]])
		#say(rStr, more=True, speak=setting("SPEAK"), moodUpdate=True)
		#YN=raw_input("")
		#if getYesNo(YN):
		YN = yesNoBox(rStr)
		if YN:
			# remove reminders
			REMINDERS[topLine] = (REMINDERS[topLine][0], REMINDERS[i][1], False)
			say("Note unchecked.", more=False, speak=setting("SPEAK"), moodUpdate=True)
			updateReminders = True


	if mode == "list":
		histCatStr=""
		for item in REMINDERS:
			checkedStr=""
			countDownStr=""
			if item[2]:
				checkedStr = "["+u'\u2713'+"]"
			elif item[1] != []:
				checkedStr = "[*]"
				countDownStr = timeDiff(toDict(item[1]), short=True)
			else:
				checkedStr = "[ ]"
			#print "\t"+checkedStr+'%10s'%(countDownStr)+" | "+item[0]
			
			#tkHistCat(checkedStr+'%10s'%(countDownStr)+" | "+item[0]+'\n')
			histCatStr += checkedStr+'%10s'%(countDownStr)+" | "+item[0]+'\n'

		if histCatStr != "":
			tkHistCat(histCatStr)
	
		if len(REMINDERS) == 0:
			say("No reminders currently saved.", more=False, speak=setting("SPEAK"), moodUpdate=True)
		
		return True


	if mode == "delete":
		#if newStr.split() == [] or k.cleanWord(newStr)=='':
		if len(matches[0]) == 0:
			#say("What reminder would you like to delete?", more=True, speak=setting("SPEAK"), moodUpdate=True)
			#newStr = raw_input("")
			newStr=questionBox("What reminder would you like to delete?")
			if newStr == "xx":
				return True
			else:
				matches[0].append(newStr)

		maxMatch=0 # calculate nearest reminder
		topLine=0 # save index of line to delete

		for i in range(len(REMINDERS)):
			matchScore = wordSim(REMINDERS[i][0], matches[0][0])
			if matchScore >= maxMatch:
				maxMatch = matchScore
				topLine=i

		rStr=processResponse("Are you sure you would like to delete: #0#?", [REMINDERS[topLine][0]])
		#say(rStr, more=True, speak=setting("SPEAK"), moodUpdate=True)
		#YN=raw_input("")
		#if getYesNo(YN):
		YN = yesNoBox(rStr)
		if YN:
			# remove reminders
			REMINDERS = REMINDERS[:topLine]+REMINDERS[topLine+1:]
			say("Note deleted.", more=False, speak=setting("SPEAK"), moodUpdate=True)
			updateReminders = True

	if mode == "purge":

		rStr="Are you sure you would like to delete all checked notes?"
		#say(rStr, more=True, speak=setting("SPEAK"), moodUpdate=True)
		#YN=raw_input("")
		#if getYesNo(YN):
		YN = yesNoBox(rStr)
		if YN:
			# remove reminders

			REMINDERS = [item for item in REMINDERS if item[2] == False]
			

			say("Checked notes deleted.", more=False, speak=setting("SPEAK"), moodUpdate=True)
			updateReminders = True	


	
	# want to overwrite ingestions file

	if updateReminders:
		f = open(DATA_DIR+'reminders.txt', 'w')
		for item in REMINDERS:
			userStr =  k.cleanWord(item[0], cleanType=1)
			f.write("\'%s\', %s, %s\n" % (userStr, item[1], item[2]))
		f.close()

	#checkReminders()

	return True
	
def checkReminders(verbose=False):

	from timeParsing import getTimeVec
	from determineFunction import updateContext
	from emotions import getFace

	rotateCircle(index=2, angle=30)

	#print "LOADING"
	REMINDERS=load(DATA_DIR+"reminders.txt", LPC=1)
	REMINDERS=[s[0] for s in REMINDERS]
	#print "LOADING... DONE"


	#nowTime = getTimeVec("now")
	updateReminders=False

	
	NowTime = datetime.datetime.now()
	NowTotalSecs = (NowTime-datetime.datetime(1970,1,1)).total_seconds()

	dueInFuture=0 # track how many are due in future

	textStr=""

	for i in range(len(REMINDERS)):
		item = REMINDERS[i]

		if item[1] != [] and item[2] != True:

			# see if the time has passes:
			
			NoteTime = datetime.datetime(year = item[1][0], month=item[1][1], day=item[1][2], hour=item[1][3], minute=item[1][4], second=item[1][5])
			NoteTotalSecs = (NoteTime-datetime.datetime(1970,1,1)).total_seconds()

			timePassed = (NowTotalSecs >= NoteTotalSecs)
		
			if not timePassed:
				dueInFuture += 1
				#say("Future: "+item[0], more=True, speak=setting("SPEAK"), moodUpdate=True)

			if timePassed:
		
				noteTD = toDict(item[1])
				
				diffStr = timeDiff(noteTD)
		
				rStr = "Reminder: "+item[0]+" (due "+diffStr+")"
		
				say(rStr, more=(not setting('SEND_TEXT')), speak=setting("SPEAK"), moodUpdate=True)
				#say("Reminder: "+item[0], more=True, speak=setting("SPEAK"), moodUpdate=True)

				REMINDERS[i] = (item[0], item[1], True)
				updateContext(inStr=item[0])
				updateReminders=True

				textStr=textStr+" <"+item[0]+">"



				
				
	

	if setting('SEND_TEXT') and not textStr == "":
		face=getFace(GLOB['MOOD'])
		moodStr=""
		if face[0]=="":
			moodStr="("+getFace(GLOB['MOOD'])[2]+")" # use the description
		else:
			moodStr=getFace(GLOB['MOOD'])[0] # use the emoticon
		
		textStr=setting("YOUR_NAME")+" "+moodStr+" REMINDER: "+textStr
		say("Sending text...", more=True, speak=False, moodUpdate=True)
		sendText(textStr)

	if verbose and not updateReminders:
		dueStr = "("+('%s'%dueInFuture)+" due in future)"
		say("No new reminders. "+dueStr, more=False, speak=setting("SPEAK"), moodUpdate=True)
		updateContext(inStr="reminders")
		return "new prompt"

	# want to overwrite ingestions file
	if updateReminders:
		f = open(DATA_DIR+'reminders.txt', 'w')
		for item in REMINDERS:
			userStr =  k.cleanWord(item[0], cleanType=1)
			f.write("\'%s\', %s, %s\n" % (userStr, item[1], item[2]))
		f.close()

	return "no prompt"

