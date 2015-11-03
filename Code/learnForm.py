from common import *
from fileIO import *


# IN CMDS
def wrongCmd(inCmd, inStr, matches=[[],[]]):
	from determineFunction import refineMatches
	#matches = refineMatches(inCmd, inStr)

	CMDHIST = GLOB['CMDHIST']
	hNum = len(CMDHIST)
	if hNum < 1:
		return True

	prevStr = CMDHIST[hNum-1-0][1]
	prevCmd = CMDHIST[hNum-1-0][2]

	intendedCmd = ""
	intendedStr = ""

	if len(matches[0]) == 1:

		intendedStr = matches[0][0]
	else:

		intendedStr = questionBox("What's an easier way to say that?")#raw_input()
		if intendedStr=="xx": intendedStr = ""

		intendedCmd = questionBox("What command is that?") #raw_input()
		if intendedCmd=="xx": intendedCmd = ""

	say("I'll remember that.", more=False, speak=setting("SPEAK"))

	prevStr = k.cleanWord(prevStr, cleanType=1)
	intendedStr = k.cleanWord(intendedStr, cleanType=1)

	# save in inputMod file:
	#   (prev inStr), (action performed)
	f = open(DATA_DIR+'corrections.txt', 'a')
	f.write("False, \'%s\', \'%s\', \'%s\'\n" % (prevCmd, prevStr, intendedStr))

	if intendedStr != "" or intendedCmd != "":
		f.write("True, \'%s\', \'%s\', \'%s\'\n" % (intendedCmd, prevStr, intendedStr))
	f.close()

	# make update immediately available
	from basicCmds import update
	update("", "", speak=False, partialChat=True, onlyChat=False)

	return True