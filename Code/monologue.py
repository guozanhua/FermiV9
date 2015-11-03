import sys
from random import *

from header import KTDIR
sys.path.insert(0, KTDIR)
from kt2 import *

VECLIST_DIR = "../VecLists/"

docList = [] # store the document to analyze?

def matchScoreOnValues(queryVecList, testVecList):
	# each vec list of of form [sentence, M12]


	if len(queryVecList[1]) != len(testVecList[1]):
		print "ERROR: vector dimension diff"
		return 0

	vecDim = len(queryVecList[1])

	diff = [queryVecList[1][i]-testVecList[1][i] for i in range(vecDim)] 
	diffSq= [diff[i]*diff[i] for i in range(vecDim)]

	dist = pow(sum(diffSq), 0.5) / (2.0*pow(vecDim, 0.5))

	if queryVecList[0] == "" or testVecList[0] == "":
		return 1.0-dist
	
	
	contextScore = similarity([queryVecList[0].split()], [testVecList[0].split()])
	#context = queryVecList[0].split()
	#for word in context:
	#	if word.lower() in testVecList[0].lower():
	#		context += 1.0

	#return (1.0-dist)+context/2.0
	rW = uniform(0.25, 0.5)
	return (1.0-dist)+rW*contextScore


def matchScoreOnWeights(importanceVec, valueVec, outlook=-1.0):
	# OUTLOOK VALUE:
	# outlook = +1:    aspiring (talking about what you want)
	# outlook = -1: complaining (talking about what you lack)

	if len(importanceVec) != len(valueVec):
		print "ERROR: vector dimension diff"
		return 0

	matchVec = [outlook*valueVec[i]*importanceVec[i] for i in range(len(valueVec))]


	#weightSum = 1.0 # sum of all 12 weights
	return sum(matchVec) #/weightSum

def gRV(inStr):

	inStr = inStr.split()

	# [("valence", normV), ("arousal",normA), ("dominance",normD)]
	VAD = affectiveRatings([inStr], normalized=True)
	VAD = [item[1] for item in VAD] # just get the values


	#print "VAD:",
	#p(VAD)


	# POSITIVES
	Mp = []
	# physical and mental health	food, shelter, work	feed, clothe, rest, work	living environment, social setting
	Mp.append(documentProperty([inStr], "health strength strong food shelter food clothe rest social live"))
	# care, adaptability, autonomy	social security, health systems, work	co-operate, plan, take care of, help	social environment, dwelling
	Mp.append(documentProperty([inStr], "care strong free autonomy secure plan safety social"))
	# respect, sense of humour, generosity, sensuality	friendships, family, relationships with nature	share, take care of, make love, express emotions	privacy, intimate spaces of togetherness
	Mp.append(documentProperty([inStr], "love respect humour generous sensual friend relationship care privacy intimate"))
	# critical capacity, curiosity, intuition	literature, teachers, policies, educational	analyse, study, meditate, investigate,	schools, families, universities, communities
	Mp.append(documentProperty([inStr], "curiosity intelligent grasp intuition literature teacher education analyse study meditate investigate school university"))
	# receptiveness, dedication, sense of humour	responsibilities, duties, work, rights	cooperate, dissent, express opinions	associations, parties, churches, neighbourhoods
	Mp.append(documentProperty([inStr], "friend dedication receptive humour responsible rights cooperate opinion association"))
	
	# imagination, tranquility, spontaneity	games, parties, peace of mind	day-dream, remember, relax, have fun	landscapes, intimate spaces, places to be alone
	Mp.append(documentProperty([inStr], "play imagine imagination tranquil game party peace dream remember relax fun intimate"))
	# imagination, boldness, inventiveness, curiosity	abilities, skills, work, techniques	invent, build, design, work, compose, interpret	spaces for expression, workshops, audiences
	Mp.append(documentProperty([inStr], "imagination imagine bold inventive curiosity skill technique invent build design compose interpret express art"))
	# sense of belonging, self-esteem, consistency	language, religions, work, customs, values, norms	get to know oneself, grow, commit oneself	places one belongs to, everyday settings
	Mp.append(documentProperty([inStr], "belong esteem consistent custom value norm oneself self grow member include"))
	
	# autonomy, passion, self-esteem, open-mindedness	equal rights	dissent, choose, run risks, develop awareness	anywhere
	Mp.append(documentProperty([inStr], "autonomy free freedom power privilege passion esteem equal choose choice aware conscious"))

	# negatives

	Mn = [] 
	Mn.append(documentProperty([inStr], "hungry poor starve sick homeless bare expose naked alone dead weak secluded"))
	Mn.append(documentProperty([inStr], "danger apathy destroy harm injure neglect weak captive insecure captive"))
	Mn.append(documentProperty([inStr], "hate disrespect sadness tragedy greedy mean enemy cold unfriendly foe apathy"))
	Mn.append(documentProperty([inStr], "confuse stupid stupidity disinterest ignorant neglect ignorance ignore forget"))
	Mn.append(documentProperty([inStr], "alone lonely enemy apathy stranger opponent insensitive incapable weak useless disagree hinder protest"))
	Mn.append(documentProperty([inStr], "gloom labor misery ignorance agitated nervous troubled worry hate discord agitation fight war tiring drudgery task"))
	
	Mn.append(documentProperty([inStr], "boring ignorance cautious shy timid dull inept unoriginal incompetence common obscure conceal hide"))
	Mn.append(documentProperty([inStr], "avoid differ disagree abandom comdemn ignore neglect insult dishonest irrational inferior fail alone"))
	Mn.append(documentProperty([inStr], "slave dependent captive confine restrain imprison handicap weak yield surrender prejudice unequal reject"))

	'''
	print "+ subsistence: ", Mp[0]
	print "+ protection: ", Mp[1]
	print "+ affection: ", Mp[2]
	print "+ understanding: ", Mp[3]
	print "+ participation: ", Mp[4]
	print "+ leisure: ", Mp[5]
	print "+ creation: ", Mp[6]
	print "+ identity: ", Mp[7]
	print "+ freedom: ", Mp[8]

	print "- subsistence: ", Mn[0]
	print "- protection: ", Mn[1]
	print "- affection: ", Mn[2]
	print "- understanding: ", Mn[3]
	print "- participation: ", Mn[4]
	print "- leisure: ", Mn[5]
	print "- creation: ", Mn[6]
	print "- identity: ", Mn[7]
	print "- freedom: ", Mn[8]
	'''

	# combine positive and negative
	# on scale from -1 to 1
	M = [Mp[i] - Mn[i] for i in range(len(Mp))]

	return VAD+M

def getTopSentence(vecList, inputVec, useWeights=False):
	#S = []

	topScore = -1.0*float('inf')
	topSentence = ""
	topVec = []

	for item in vecList:
		score=0
		if useWeights:
			score = matchScoreOnWeights(inputVec, item[1], outlook=-1.0)
		else:
			score = matchScoreOnValues(inputVec, item)

		if score >= topScore:
			topScore = score
			topSentence = item[0]
			topVec = item[1]

	return [topSentence.replace('\\', ''), topScore, topVec]

# TODO: replace with call to load in loadFile.py
def loadVecList(fileName, LPC=1, addQuotes=False):
	CMDList=[]

	with open (fileName) as f:
		lines = f.readlines()
		cmd=[] # store command text to be processed
		pos = 0 # increments mod linesPerCmd
				# so we know when cmd is ready to be processed
		cmdNum=0 # number of commands from commands file

		i=0
		while i < len(lines):
			line = lines[i]
			while line == '\n':
				i += 1
				if i >= len(lines):
					break
				line=lines[i]
			i += 1

			if pos == 0:
				cmd=[]

			if addQuotes:
				cmd.append('\''+line.replace('\n', '').replace('\'','')+'\'')
			else:
				cmd.append(line.replace('\n', ''))

			pos += 1
			pos = pos%LPC # linesPerCmd lines per command

			# process cmd to append to CMD
			if pos == 0:
				CMDList.append([[] for c in range(LPC)])
				for j in range(LPC):
					CMDList[cmdNum][j] = eval(cmd[j]) # function name

				cmdNum += 1

	CMDList = [item[0] for item in CMDList]
	return CMDList


def output(vecList, fileName):
	f = open(VECLIST_DIR+fileName, 'w')
	for item in vecList:
		f.write('%s'%item)
		f.write('\n')
	f.close()

def saveDocVecs(doc, docName):
	V = []
	print "CALCULATING..."
	for i in range(len(doc)):
		print i, len(doc)
		sentence = ' '.join(doc[i])

		vec = gRV(sentence)

		cleanSentence = cleanWord(sentence, cleanType=1)

		V.append([cleanSentence, vec])

	output(V, docName)
		


#if __name__ == "__main__":


	# load sources
	#global docList

	#docList.append(learn("cats"))

	#wordWeb(docList[0])
	'''
	importanceVec =[0.0, #   valence
					0.0, #   arousal
					0.0, #   dominance ____
					0.0, # subsistence
					1.0, # protection
					1.0, # affection
					0.0, # understanding
					0.0, # participation
					0.0, # leisure
					0.0, # creation
					0.0, # identity
					1.0] # freedom
	'''


#QUOTES = loadData('../Database/Quotes/quotes.txt')
#QUOTES = ' '.join(QUOTES)
#QDoc = loadString(QUOTES)
#saveDocVecs(QDoc, '../VecLists/quotes_1.txt')

#QV = loadVecList('../VecLists/quotes_1.txt')
