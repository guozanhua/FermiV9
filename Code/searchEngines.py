from header import *
from common import *
from graphics import *

timeoutDur=7

def urlify(inStr, space='+'):
	
	
	inStr = inStr.replace('+', '%2B')
	inStr = inStr.replace('(', '%28')
	inStr = inStr.replace(')', '%29')
	inStr = inStr.replace('=', '%3D')
	

	inStr = inStr.replace(' ', space)

	return inStr

def parseWolframString(inStr):
	inStr = '\n'.join(inStr.split("\\n"))

	inStr = inStr.split('"stringified": "', 1)[1]
	inStr = inStr.split('","mInput"', 1)[0]
	#print retStr
	
	inStr = inStr.replace('&times;', '*')
	inStr = inStr.replace('\/', '/')
	#inStr = inStr.replace('|', '=')
	inStr = inStr.replace('  ', ' ')

	inStr = inStr.replace("(data not available)", "")
	#print "returned", retStr
	return inStr

@timeout(timeoutDur)
def getWolframAnswer(inStr):
	# get info from www.wolframalpha.com/input/?i=inStr

	html="http://www.wolframalpha.com/input/?i="+urlify(inStr, space='+')


	try:
		soup = BeautifulSoup(urllib2.urlopen(html).read())
	except:
		return ""
	#print "soup: ", len(soup)

	success = False
	retStr=""
	
	testList = [["dd", "conditions"],
				["span", "temp"]]
	
	for match in testList:
		try:
			retStr += soup.find(match[0],{'class':match[1]}).text + '\t'
			success = True
		except:
			pass


	if success: 
		#print "returned", retStr
		return retStr
	


	soupTxt2 = soup.text
	soupTxt2 = soupTxt2.split('\n')

	restate=""
	for item in soupTxt2:
		if "pod_0100.push" in item:
			#print "found item"
			restate = item

	for item in soupTxt2:
		if "pod_0200.push" in item:
			#print "found item"
			retStr = item

	if retStr == "":
		for item in soupTxt2:
			if "pod_0400.push" in item:
				#print "found item"
				retStr = item
	
	#print "retStr: "+retStr

	if retStr == "": return retStr

	# now need to extract answer from string
	restate = parseWolframString(restate)

	retStr = parseWolframString(retStr)
	#print "returned", retStr

	if restate != "":
		restate = restate.replace('\n', ', ')
		return restate+'\n\t'+retStr
	else:
		return retStr

@timeout(timeoutDur)
def getBingAnswer(inStr):
	# get info from http://www.answers.com/Q/inStr&isLookUp=1#Q=inStr

	inStr = k.cleanWord(inStr.lower())
	#print "instr", inStr

	html="http://www.answers.com/Q/"+inStr.replace(' ', '_')+'&isLookUp=1#Q='+inStr.lower().replace(' ', '%20')
	
	try:
		htmlText = urllib2.urlopen(html).read()
	except:
		return ""
	htmlText = re.sub('<br />','\n',htmlText)
	htmlText = re.sub('\n\n','\n',htmlText)
	htmlText = re.sub('<li>','<li> ',htmlText)

	soup = BeautifulSoup(htmlText)
	
	success = False

	testList = [["div", "answer_text"]]#,
				#["div", "content_text"]]
	retStr=""
	for match in testList:
		try:
			retStr = soup.find(match[0],{'class':match[1]}).text
			retStr = retStr.lstrip()
			retStr = retStr.replace("Creative and Original Answers:", "")
			retStr = retStr.replace("(Wikipedia)", "")
			retStr = retStr.split("For the source and more detailed information", 1)[0]
			retStr = retStr.rstrip()

			#print len(retStr)
			
			return retStr
		except:
			pass

		

	return retStr

@timeout(timeoutDur+30)
def getWikiHowAnswer(inStr):
	# http://www.wikihow.com/Special:GoogSearch?cx=008953293426798287586%3Amr-gwotjmbs&cof=FORID%3A10&ie=UTF-8&q=how+to+bake+a+cake
	inStr = k.cleanWord(inStr.lower())
	inStr = inStr.lstrip()
	inStr = inStr.rstrip()
	#print "instr", inStr

	#inStr2 = inStr.split()

	urlBase='http://www.wikihow.com/Special:GoogSearch?cx=008953293426798287586%3Amr-gwotjmbs&cof=FORID%3A10&ie=UTF-8&q='
	url=urlBase+inStr.replace(' ', '+')
	url=url.replace('&', '\&')

	#print "url: ", url

	

	rStr="Would you like to search wikiHow for "+inStr+"?"
	#say(rStr, more=True, speak=setting("SPEAK"), moodUpdate=True)
	YN=yesNoBox(rStr) #raw_input("")
	if YN: #getYesNo(YN):
		cmdStr=setting("WEB_BROWSER")+" "+url+" > /dev/null 2>&1 &"
		try:
			subprocess.call(cmdStr, shell=True)
		except:
			pass
			return ""
		return "Opening wikiHow page."
	return ""

@timeout(timeoutDur)
def getEviAnswer(inStr):
	# get info from www.evi.com/q/inStr


	testList = [["h3", "tk_text"],
				["div", "tk_text"],
				["div", "tk_object"],
				["div", "tk_common"], 
				["p", "unique_translation"],
				["div", "tk_yesno"]]

	html="https://www.evi.com/q/"+inStr.replace(' ', '_')

	try:
		soup = BeautifulSoup(urllib2.urlopen(html).read())
	except:
		pass
		return ""

	success = False
	for match in testList:
		try:
			retStr = soup.find(match[0],{'class':match[1]}).text
			retStr = retStr.lstrip()
			retStr = retStr.replace('\n', '').replace('..','.')
			retStr = retStr.replace('\t', '')
			retStr = retStr.replace("Evi", setting("AI_NAME"))
			retStr = retStr.replace(" (pronounced eevee)", '')
			#retStr = retStr+" (Evi)"
			return retStr
		except:
			pass
		

	return ""

