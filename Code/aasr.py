import difflib
import json
from random import *
import copy
from textblob import TextBlob
import sys
from fileIO import jsonLoad, jsonSave

from phraseModify import addAuxVerb, listize, removeStrange, wordSim, processResponse

sys.path.append("..")
from patterns_lib.patternMatching import matchFromList

from header import KTDIR
sys.path.insert(0, KTDIR)
import kt2 as k

W5 = jsonLoad('w5_4.txt')

DEBUG = False

def clearlyQuestion(inStr):

	inStr = inStr.strip()
	if inStr[len(inStr)-1] == '?':
		return True

	# check that the first word is not a 5W
	inStrWords = inStr.lower().split()

	for word in inStrWords:
		if word in ["who", "what", "where", "when", "why", "how", "whose"]:
			return True
	if inStrWords[0] == "is": return True

	return False

def formAnswerString(answers):#, qType):
	global W5

	if answers == [["","","",0]]: return ''

	rCombo = []

	for a in answers:
		
		if a[1]=='': continue
		# response format
		# query subtopic stored in a[1] (ex. "What Who", "How", "PrKr")
		format = W5[a[1]]['aformat']


		#rCombo.append(processResponse(format, [a[0],a[2]]).capitalize())
		if format == "":
			rStr = addAuxVerb(a[0], nextStr = a[2])+' '+a[2]+'(%s).'%round(a[3], 2)
			rCombo.append(rStr.capitalize())
		else:
			rCombo.append(processResponse(format, [a[0],a[2]]).capitalize())



	return ' '.join(rCombo)

def getMatchScore(answer, query="", matches=[[],[]]):

	# check if answer[2] is the answer to query
	# which means comparing answer[0&1] to query/matches

	query = query.replace('?', '')
	# answer = [topic, subtopic, answer string]

	# case 0: no query or matches
	if query == "" and matches==[[],[]]:
		print "no query or matches"
		return 0

	# case 1: only query, no matches
	if query != "" and matches==[[],[]]:
		#print "CASE 1"
		# ex. "who is my brother"
		# answer = ["my brother", "What Who", "Kyle"]

		# ex. "is kyle my brother"
		# answer = ["my brother", "What Who", "Kyle"]

		qWords = query.lower().split()
		aWords = []
		for item in answer[0:2]:
			aWords.extend(item.lower().split())

		sA, sQ = set(aWords), set(qWords)
		shareWords=len(list(sA & sQ))
		pctShared = shareWords*2.0 / (len(sA) + len(sQ))

		kScore = k.similarity([aWords], [qWords])

		score = pctShared*0.5 + kScore*0.5
		
		'''
		print "aWords:", aWords
		print "qWords:", qWords
		print "sA:", sA
		print "sQ:", sQ
		print "\tscore:", score
		'''
		return score

	# case 2: only matches, no query
	if query == "" and matches!=[[],[]]:
		#print "CASE 2"
		# ex. [["my brother"], ["who", "is"]]
		# answer = ["my brother", "What Who", "Kyle"]


		qWords = []
		for item in matches:
			for a in item:
				qWords.extend(a.lower().split())
		
		aWords = []
		for item in answer[0:2]:
			aWords.extend(item.lower().split())

		sA, sQ = set(aWords), set(qWords)
		shareWords=len(list(sA & sQ))
		pctShared = shareWords*2.0 / (len(sA) + len(sQ))

		kScore = k.similarity([aWords], [qWords])

		score = pctShared*0.5 + kScore*0.5
		
		'''
		print "aWords:", aWords
		print "qWords:", qWords
		print "sA:", sA
		print "sQ:", sQ
		print "\tscore:", score
		'''
		return score

	# case 3: matches and query
	if query != "" and matches!=[[],[]]:
		#print "CASE 3"

		qWords = query.lower().split()
		for item in matches:
			for a in item:
				qWords.extend(a.lower().split())
		
		aWords = []
		for item in answer[0:2]:
			aWords.extend(item.lower().split())

		sA, sQ = set(aWords), set(qWords)
		shareWords=len(list(sA & sQ))
		pctShared = shareWords*2.0 / (len(sA) + len(sQ))

		kScore = k.similarity([aWords], [qWords])

		score = pctShared*0.5 + kScore*0.5
		
		'''
		print "aWords:", aWords
		print "qWords:", qWords
		print "sA:", sA
		print "sQ:", sQ
		print "\tscore:", score
		'''
		return score


	print "none of 4 choices"
	return 0

def queryFacts(query, factList, qType="", matches=[[],[]], topOne=False, minScore=0.4):
	# query: the original user string
	# factList: database of facts
	# qType: kind of query (ex. WhatWho, WhereWhen, Why, etc.)
	# matches: matches of best query type:
	#	ex. "[who] [is] {my brother}" -> [["my brother"], ["who", "is"]]

	topMatches=[] # store all good matches
	answerListEps = 0.05
	if topOne:
		answerListEps = 0.0
	topScore = 0

	for tK in factList: # for each topic
		for qK in factList[tK]: # for each sub-topic in the topic
			for a in factList[tK][qK]: # for each answer in that sub-topic
				
				score = 0
				match = ["","",""]

				score1 = getMatchScore(answer=[tK, qK, a], query=query, matches=matches)
				score2 = getMatchScore(answer=[a, qK, tK], query=query, matches=matches)


				score = max(score1, score2)
				match = [tK, qK, a, score1]

				
				if score != 0.0 and DEBUG:
					print "answer:", [tK, qK, a]
					print "query:", query
					print "matches:", matches
					print "\tscore:", score
				
				if score >= topScore-answerListEps:

					if score > topScore+answerListEps:
						topScore = score
						topMatches = [match]
					else:
						topMatches.append(match)
					

	if topMatches == [] or topScore <= minScore:
		topMatches = [["","","",0]]
	return topMatches

def tagQuery(tag, factList):
	#print "tag:", tag
	answers = []
	for tK in factList: # for each topic
		tKScore = wordSim(tag, tK, basic=True)
		for qK in factList[tK]: # for each sub-topic in the topic
			qKScore = wordSim(tag, qK, basic=True)
			for a in factList[tK][qK]:
				aScore = wordSim(tag, a, basic=True)

				score = max(tKScore, qKScore, aScore)
				if score >= 0.9:
					#print "adding:", [tK, qK, a, score]
					answers.append([tK, qK, a, 1.0])

	return answers

def addToFacts(factList, fact, replaceInfo=False):
	# fact ex. ["apples", "what who", "red"]

	# want:
	# 	factList["apples"]["what who"] = "red"

	sub = fact[0]
	wType=fact[1]
	prop = fact[2]

	# make sure fact topic already in dictionary
	inDict = False
	for key in factList:
		#if sub.lower() == key.lower():
		if wordSim(sub.lower(), key.lower(), basic=True) > 0.95:
			sub = key
			inDict = True
			break
	if not inDict:
		factList[sub] = {}

	# check if subtopic is in dictionary
	inSubDict=False
	for key in factList[sub]:
		if wType.lower() == key.lower():
			wType = key
			inSubDict=True
			break
	if not inSubDict:
		factList[sub][wType] = []

	if replaceInfo:
		factList[sub][wType] = prop
	else:
		factList[sub][wType].append(prop)	



	return

def handleInput(inStr, factList, factFileName, getContext=False, queries=True, save=False):
	global W5


	inStr = removeStrange(inStr).strip()
	#print "HANDLING:", inStr

	if "tag:" == inStr.split()[0]:
		tagStr = inStr.lower().replace('tag: ', '')
		retStr = formAnswerString(tagQuery(tag=tagStr, factList=factList))
		return retStr, tagStr, "add"


	topMatches = []
	topWType = []

	topConfidence = 0
	inputType = "add"

	for wK in W5:
		matches_add, confidence_add =     matchFromList(W5[wK]['add'], inStr, trials=10, subTrials=150, includeLenScore=True)
		matches_query, confidence_query = matchFromList(W5[wK]['query'], inStr, trials=10, subTrials=150, includeLenScore=True)

		if DEBUG:
			print "clearlyQuestion:", clearlyQuestion(inStr)
			print matches_add, confidence_add
			print matches_query, confidence_query

		if confidence_add >= topConfidence and not clearlyQuestion(inStr):
			topConfidence = confidence_add

			topMatches = matches_add
			topWType = wK
			inputType = "add"

			#print matches_add, confidence_add

		elif confidence_query > topConfidence:
			topConfidence = confidence_query

			topMatches = matches_query
			topWType = wK
			inputType = "query"

			#print matches_query, confidence_query


	if topMatches == [] or (inputType=="add" and len(topMatches[0]) < 2) or topConfidence < 0.95:
		# no good match found, so return default
		#print "here"
		#print topConfidence
		return "", "", ""


	retStr = ""	
	context=""

	dataChanged = False

	if inputType == "add":
		# ex. what(sub) = prob
		sub = topMatches[0][0]
		prop = topMatches[0][1]

		replaceInfo = "just" in topMatches[1] or "only" in topMatches[1]

		retStr="Adding to factual memory:\n"+'['+topWType+']'+'('+sub+') = '+prop
		
		fact = [sub, topWType, prop] # ex. ["apples", "what who", "red"]
		addToFacts(factList, fact, replaceInfo=replaceInfo)

		dataChanged = True
		context = prop

	elif inputType == "query" and queries:

		answers=queryFacts(factList=factList, query=inStr, qType=topWType, matches=topMatches, minScore=0.3)

		#print "ANSWERS:", answers
		retStr = formAnswerString(answers)#, qType=topWType)

		if len(answers[0]) != 0:
			context = answers[0][2]


	if save and dataChanged:
		jsonSave(factList, factFileName)


	return retStr, context, inputType

def interrogation(qSeed="Where are the other drugs going?", numQ = 5):

	return


#print "W5:", W5

if __name__ == "__main__":

	factFileName = "question_lib/testdata.txt"

	W5 = jsonLoad('w5_4.txt')

	factList = jsonLoad(factFileName)

	DEBUG =True

	inStr = ""

	while inStr != "exit":

		sys.stdout.write('>> ')
		inStr = raw_input("")

		print handleInput(inStr=inStr, factList=factList, factFileName=factFileName, save=True)

	jsonSave(factList, factFileName)


	'''
	file = open('raw_text.txt')
	t=file.read()
	TB = TextBlob(t)
	TS = [item.raw for item in TB.sentences]

	for i in range(len(TS)):
		s = TS[i]
		print i+1, "/", len(TS)
		handleInput(inStr=s, factList=factList, factFileName=factFileName)

		if i >= 50: break

	jsonSave(factList, factFileName)
	'''