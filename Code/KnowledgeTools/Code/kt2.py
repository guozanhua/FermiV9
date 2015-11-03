import subprocess
import difflib		# for string similarity
import nltk.data
import nltk
import collections # to get unique words and their frequencies
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn
import sys
import pprint # pretty print
import math
from igraph import *
import copy
import csv # to read data files
from random import *
import Tkinter as tk # for clipboard copying
import signal # for watching for timeouts from web scrapes

import painter
import unicodedata

# store stop words globally
STOP=[]
ARATINGS=[]
CODE_DIR="/home/tanner/Dropbox/sandbox/FermiV9/Code/KnowledgeTools/Code/"
DOCS_DIR="/home/tanner/Dropbox/sandbox/FermiV9/Code/KnowledgeTools/Docs/"

'''
structes worked with:
	- sentence lists
	- word frequency lists
'''

QUIET=True


class TimedOutExc(Exception):
	"""
	Raised when a timeout happens
	"""

def timeout(timeout):
	"""
	Return a decorator that raises a TimedOutExc exception
	after timeout seconds, if the decorated function did not return.
	"""

	def decorate(f):

		def handler(signum, frame):
			raise TimedOutExc()

		def new_f(*args, **kwargs):

			old_handler = signal.signal(signal.SIGALRM, handler)
			signal.alarm(timeout)

			result = f(*args, **kwargs)  # f() always returns, in this scheme

			signal.signal(signal.SIGALRM, old_handler)  # Old signal handler is restored
			signal.alarm(0)  # Alarm removed

			return result

		new_f.func_name = f.func_name
		return new_f

	return decorate


def learn(topic):

	try:
		D = loadDoc(topic)
		return D

	except TimedOutExc:
		pass
		return []


@timeout(10)
def loadDoc(topic):
	docName=""
	if "." in topic:
		#docName="~/Dropbox/sandbox/KnowledgeTools/Docs/"+topic
		docName=topic
	else:
		# call bash script to get and fix wiki article

		cmd="bash "+CODE_DIR+"loader.sh "+'"'+topic.replace(' ', '_')+'"'


		#cmd="bash loader.sh \""+topic.replace+"\""
		#print "CMD =", cmd
		#subprocess.Popen(cmd)
		
		#process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
		#output = process.communicate()[0]

		subprocess.call(cmd, shell=True)


		docName=DOCS_DIR+topic.lower().replace(' ', '_')+".txt"


	tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

	data=[]
	with open(docName) as f:
		while True:
			c = f.read(1)
			if not c:
				break
			
			if ord(c) < 32 or ord(c) > 126:
				data.append(' ')
			else:
				data.append(c)
			

	data = ''.join(data)

	parsedData = tokenizer.tokenize(data)
	newParsedData = [sentence.split() for sentence in parsedData]

	return newParsedData

def loadData(topic):
	docName=""
	if ".txt" in topic:
		#docName="~/Dropbox/sandbox/KnowledgeTools/Docs/"+topic
		docName=topic
	else:
		# call bash script to get and fix wiki article
		cmd="bash loader.sh "+topic.replace(' ', '_')
		#subprocess.Popen(cmd)
		process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
		output = process.communicate()[0]

		docName=DOCS_DIR+topic.replace(' ', '_')+".txt"

	# open document and parse into sentences and words

	
	data=[]
	with open (docName) as f:
		lines = f.readlines()
		for line in lines:
			words = line.split()
			for word in words:
				data.append(word)
				#print (word)


	# return word array for article
	return data


def loadString(string):
	tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

	string = cleanWord(string, cleanType=2)

	parsedData = tokenizer.tokenize(string)
	newParsedData = [sentence.split() for sentence in parsedData]



	return newParsedData


def loadClipboard():
	root = tk.Tk()
	# keep the window from showing
	root.withdraw()

	# read the clipboard
	c = root.clipboard_get()
	try:
		c = unicodedata.normalize('NFKD', unicode(c)).encode('ascii','ignore')
	except:
		pass
	return loadString(c)

def lemmatizer(string, lemType=1):
	string = string.split()

	try:
		newString=[]
		for word in string:
			if lemType == 1:
				lmtzr = WordNetLemmatizer()
				word = lmtzr.lemmatize(word, 'n')
				word = lmtzr.lemmatize(word, 'v')
				word = lmtzr.lemmatize(word, 'r')
				word = lmtzr.lemmatize(word, 's')
				word = lmtzr.lemmatize(word, 'a')
			else:
				stemmer = SnowballStemmer("english")
				word=stemmer.stem(word)

			newString.append(word)
	except:
		#print "LEMMATIZER ERROR"
		pass
		return ' '.join(string)

	return ' '.join(newString)

def cleanWord(word, cleanType=0):

	if cleanType == 0:
		#word = unicodedata.normalize('NFKD', unicode(word)).encode('ascii','ignore')

		word = word.lower()
		word = word.replace('\'s', '')
		word = word.replace(',', '')
		word = word.replace('.', '')
		word = word.replace(')', '')
		word = word.replace('(', '')
		word = word.replace('?', '')
		word = word.replace('!', '')
		word = word.replace(':', '')
		word = word.replace('\"', '')

		toRemove = []
		for char in word:
			# 32 -> 126
			if ord(char) not in range(32, 122+1):
				toRemove.append(char)
		toRemove = list(set(toRemove))

		for char in toRemove:
			#print "removed:", char
			word = word.replace(char, '')


	elif cleanType == 1:

		#word = unicodedata.normalize('NFKD', unicode(word)).encode('ascii','ignore')

		#word = word.lower()
		word = word.replace('\\', '')
		#word = word.replace('\'s', '')
		word = word.replace('\'', "\\'")
		#word = word.replace(',', '')
		#word = word.replace('.', '')
		#word = word.replace(')', '')
		#word = word.replace('(', '')
		#word = word.replace('?', '')
		#word = word.replace('!', '')
		#word = word.replace(':', '')
		#word = word.replace('\"', '')

		word = word.lstrip()
		word = word.rstrip()
	elif cleanType == 2:
		word = word.replace('\n', ' ')
		# just get rid of non alpha-numeric chars

		#word = unicodedata.normalize('NFKD', unicode(word)).encode('ascii','ignore')

		toRemove = []
		for char in word:
			# 32 -> 126
			if ord(char) not in range(32, 126+1):
				toRemove.append(char)
		toRemove = list(set(toRemove))

		for char in toRemove:
			#print "removed:", char
			word = word.replace(char, '')
	elif cleanType == 3:
		#try:
		#	word = unicodedata.normalize('NFKD', unicode(word)).encode('ascii','ignore')
		#except:

		
		word = word.replace('\n', 'XNEWLINEX')
		toRemove = []
		for char in word:
			# 32 -> 126
			if ord(char) not in range(32, 126+1):
				toRemove.append(char)
		toRemove = list(set(toRemove))

		for char in toRemove:
			#print "removed:", char
			word = word.replace(char, '')

		word = word.replace('XNEWLINEX', '\n')
		
		

	return word


def filter(doc, lemmatize=False, lemType=1, removeStops=True):

	newDoc=[]
	
	#stop=loadData("stopwords.txt")
	#stop = stopwords.words('english')
	#lmtzr = WordNetLemmatizer()
	
	#j v n r

	for i in range(len(doc)):
		#newDoc.append([lmtzr.lemmatize(lmtzr.lemmatize(word.lower().replace('\'s', '').replace(',', '')), 'v')
		#	for word in doc[i] if word.lower() not in stop])

		if lemmatize == True:
			newDoc.append([lemmatizer(cleanWord(word), lemType=lemType) 
				for word in doc[i] if (lemmatizer(cleanWord(word), lemType=1) not in STOP or not removeStops)])
		else:
			#newDoc.append([cleanWord(word) for word in doc[i] if (cleanWord(word) not in STOP or not removeStops)])
			newSen = [cleanWord(word) for word in doc[i] if (cleanWord(word) not in STOP or not removeStops)]
			newSen = [sen for sen in newSen if sen != '']
			newDoc.append(newSen)
	


	# return filtered word array
	return newDoc

def synonyms(word, wType="any"):
	syn_set = []
	if wType == "any":
		for synset in wn.synsets(word):
			for item in synset.lemma_names():
				syn_set.append(item)
		return syn_set
	else:
		for synset in wn.synsets(word, wType):
			for item in synset.lemma_names():
				syn_set.append(item)
		return syn_set

def wordsRelated(wordA, wordB, ignoreStop=True):
	# two words are related if their sets of lemmatized synonyms have an intersection
	wordA = wordA.lower()
	wordB = wordB.lower()

	if wordA in STOP or wordB in STOP: return False

	Asyns=[]
	Bsyns=[]
	
	Asyns = synonyms(wordA)
	Bsyns = synonyms(wordB)

	Asyns = set(filter([Asyns], lemmatize=True, lemType=2)[0])
	Bsyns = set(filter([Bsyns], lemmatize=True, lemType=2)[0])

	#print Asyns & Bsyns
	return len(Asyns & Bsyns) >= 1

def wordRareness(word):

	if word.strip() == "":
		return 1.0



	if len(word.split()) > 1:
		lens = [wordRareness(a) for a in word.split()]
		#lens.sort()
		return 1.0*sum(lens) / len(lens)
		#return min(lens)

	if word.lower() in STOP:
		return 0.0

	syns = wn.synsets(word)
	countSum = 0
	for s in syns:
		for l in s.lemmas():
			countSum += l.count()
			#print l.name(), l.count()

	return pow(2.0, -1.0*countSum/300.0)

def tagSentence(sen):
	# sentence must be list of words
	return nltk.pos_tag(sen)


def testing(): #param, param2):
	#print "testing with ", param
	print "AB: ", documentSimilarity(A, B)#, param, param2)
	print "CD: ", documentSimilarity(C, D)#, param, param2)
	print "AC: ", documentSimilarity(A, C)#, param, param2)
	print "AD: ", documentSimilarity(A, D)#, param, param2)
	print "BC: ", documentSimilarity(B, C)#, param, param2)
	print "BD: ", documentSimilarity(B, D)#, param, param2)
	print "PA: ", documentSimilarity(P, A)#, param, param2)
	print "PB: ", documentSimilarity(P, B)#, param, param2)
	print "PC: ", documentSimilarity(P, C)#, param, param2)
	print "PD: ", documentSimilarity(P, D)#, param, param2)

def help():
	print "\n=================================================\n"
	print "DOC   = learn(\"topic name/file name\")"
	print "DOC   = filter(DOC)"
	print
	print "DOC   = intersection(DOC_A, DOC_B)"
	print "DOC   = union(DOC_A, DOC_B)"
	print "DOC   = removeFrom(DOC_A, DOC_B)"
	print
	print "STATS = wordIntersection(DOC_A, DOC_B)"
	print "STATS = getWordFreqs(DOC)"
	print "SCORE = documentSimilarity(DOC_A, DOC_B)"
	print "STRS  = queryDocument(DOC, STRING)"
	print "SCORE = documentProperty(DOC, \"STRING\")"
	print "        properties(DOC)"
	print "        comparisonSummary(DOC_A, DOC_B)"
	print "        documentSummary(DOC)"
	print "        wordWeb(DOC, V_NUM, E_NUM, edgeType)"
	print "STRS  = wordTags(DOC, POS=\"NN\", \"JJ\", etc.)"
	print "STRS  = importantSentences(DOC, SEN_NUM)"
	print "        paintImage(DOC)"
	print "VAD   = affectiveRatings(DOC)"
	print "\n=================================================\n"

def p(data):
	pp = pprint.PrettyPrinter(indent=4)
	pp.pprint(data)

def sf(x, digits=3):
	strDig= '%s' % digits
	gm="%."+strDig+'g'
	return float(gm % x)


def intersection(docA, docB, threshold=0.0025, fromA=True, fromB=True, removeTops=False):
	''' return sentences from A and B that have a key word from both A and B '''

	
	if len(docB) <= 1: threshold = 0
	

	Afiltered=filter(docA, lemmatize=True, lemType=2)

	Bfiltered = filter(docB, lemmatize=True, lemType=2)

	#ABset = wordIntersection(docA, docB)
	#ABset = [word[0] for word in ABset if word[1] >= threshold]
	ABset = wordIntersection(Afiltered, Bfiltered)
	ABset = [word[0] for word in ABset if word[1] >= threshold]

	Afreqs = getWordFreqs(Afiltered)
	Bfreqs = getWordFreqs(Bfiltered)

	newDoc=[]

	if fromA == True:
		for i in range(len(docA)):
			if bool(set(ABset) & set(Afiltered[i])) == True:
				newDoc.append(docA[i])

	if fromB == True:
		for i in range(len(docB)):
			if bool(set(ABset) & set(Bfiltered[i])) == True:
				newDoc.append(docB[i])

	if removeTops == True:
		return removeFrom(removeFrom(newDoc, docA, threshold=Afreqs[0][1]*0.5), docB, threshold=Bfreqs[0][1]*0.5)
	else:
		return newDoc

def union(docA, docB):
	''' return esntences from A and B '''
	
	newDoc=[]

	for sentence in docA:
		newDoc.append(sentence)

	for sentence in docB:
		newDoc.append(sentence)
	
	return newDoc

def removeFrom(docA, docB, threshold=0.0025):
	''' return sentences from A that don't have a key word from B '''
	
	Bset = getWordFreqs(filter(docB, lemmatize=True, lemType=2))
	Bset = [word[0] for word in Bset if word[1] >= threshold]

	Afiltered=filter(docA, lemmatize=True, lemType=2)
	newDoc=[]


	for i in range(len(docA)):
		if bool(set(Bset) & set(Afiltered[i])) == False:
			newDoc.append(docA[i])
		'''
		for word in Bset:
			if word[0] in Afiltered[i] and word[1] >= threshold:
				newDoc.append(docA[i])
				break;
		'''
		# add sentence if intersection with Bset empty

	return newDoc

def wordIntersection(docA, docB):
	Ap = getWordFreqs(filter(docA, lemmatize=True, lemType=1))
	Bp = getWordFreqs(filter(docB, lemmatize=True, lemType=1))
	ABUniq = intersectFreqs(Ap, Bp)
	ABUniq.sort(key=lambda tup: tup[1])
	ABUniq.reverse()
	return ABUniq


def intersectFreqs(uniqA, uniqB):

	newUniq = []

	for itemA in uniqA:
		for itemB in uniqB:

			if itemA[0] == itemB[0]:

				fA = itemA[1]
				fB = itemB[1]
				newF = min(fA, fB) #pow(fA*fB, 0.5) #fA * fB/(max(fA, fB))
				newUniq.append((itemA[0], newF))

	newUniq.sort(key=lambda tup: tup[1])
	return newUniq

def getWordFreqs(doc):
	wordList=[item for sublist in doc for item in sublist]

	counter=collections.Counter(wordList)
	freqs = counter.values()
	words = counter.keys()

	# sort list by frequency from highest to lowest
	combo=[(words[i], freqs[i]) for i in range(len(words))]
	combo.sort(key=lambda tup: tup[1])
	combo.reverse()
	totalWords=sum(n for _, n in combo)
	#maxCount=max(n for _, n in combo)
	combo=[(combo[i][0], combo[i][1]*1.0/totalWords) for i in range(len(combo))]
	#combo=[(combo[i][0], combo[i][1]*1.0/maxCount) for i in range(len(combo))]

	#combo=[(combo[i][0], i) for i in range(len(combo))]

	return combo


def wordWeb(doc, V_NUM=30, E_NUM=30, edgeType="adjacent"):
	
	#Algorithm:
	#	- split document into unique non-stop words
	#	- for each pair of words, find how often they occur in the same sentence
	#		- interpret as edge weightType
	#	- add top K words and top N edges
	

	filteredDoc=filter(doc, lemmatize=True, lemType=1)

	# unique non-stop words with frequencies
	wordFreqs=getWordFreqs(filteredDoc)[0:V_NUM]

	# get number of sentences each word occurs in separately
	wordSenCounts = []

	# get total number of times each word occurs in document
	wordTotCounts=[]

	for word in wordFreqs:
		senCount = 0
		totCount = 0
		for sentence in filteredDoc:
				if word[0] in sentence: 
					senCount += 1
					totCount += len([k for k, l in enumerate(sentence) if l == word[0]])


		#print word[0], "count = ", count
		wordSenCounts.append(senCount)
		wordTotCounts.append(totCount)

	edgeList = []

	if edgeType == "sentence":
		for i in range(len(wordFreqs)):
			for j in range(i+1, len(wordFreqs)):

				# find num sentences where they appear together
				wA = wordFreqs[i]
				wB = wordFreqs[j]

				count = 0

				for sentence in filteredDoc:
					if (wA[0] in sentence) and (wB[0] in sentence): 
						count += 1

				# calculate distance factor
				#   = 1 - 2*intersection / (size A + size B)
				#print wordFreqs[i], ", ", wordFreqs[j]
				D = 1.0 - 2.0*count / (wordSenCounts[i] + wordSenCounts[j])

				# calculate edge weight
				I = 100.0 * min(wA[1], wB[1])
				I_hat = 100.0*I / len(wordFreqs)
				W = I_hat * math.log(I_hat + 1.0) * (1.0 - D)
				#edgeList.append((wA[0], wB[0], W))
				if W != 0: edgeList.append((i, j, W))
	else: # edgeType == "adjacent"
		
		#Algorith,:
		#	- for each pair of words wA, wB in wordFreqs:
		#		- find how often they occur in the same sentence, beside eachother
		
		for i in range(len(wordFreqs)):
			for j in range(i+1, len(wordFreqs)):

				# find num sentences where they appear together
				wA = wordFreqs[i]
				wB = wordFreqs[j]

				count = 0

				for sentence in filteredDoc:
					if (wA[0] in sentence) and (wB[0] in sentence): 
						locsA = [k for k, l in enumerate(sentence) if l == wA[0]]
						locsB = [k for k, l in enumerate(sentence) if l == wB[0]]

						# add one
						locsAp = [k+1 for k in locsA if k+1 in range(len(sentence))]
						# subtract one
						locsAm = [k-1 for k in locsA if k-1 in range(len(sentence))]
						# all valid position that are next to wA
						locsAb = locsAp+locsAm

						# number of times wA is next to wB in the sentence
						count += len(list(set(locsAb) & set(locsB)))

				# calculate distance factor
				#   = 1 - 2*intersection / (size A + size B)
				# print "i=",i, ", ", "j=", j
				D = 1.0 - 2.0*count / (wordTotCounts[i] + wordTotCounts[j])

				# calculate edge weight
				I = 100.0 * min(wA[1], wB[1])
				I_hat = 100.0*I / len(wordFreqs)
				W = I_hat * math.log(I_hat + 1.0) * (1.0 - D)
				#edgeList.append((wA[0], wB[0], W))
				if W != 0: edgeList.append((i, j, W))

	
	edgeList.sort(key=lambda tup: tup[2])
	edgeList.reverse()

	g=Graph()
	g.es["weight"]=1.0 # make it a weighted edge graph

	# add vertices
	for i in range(len(wordFreqs)):
		g.add_vertex(i)

	# add vertex labels
	#vLabels = [item[0] for item in wordFreqs]
	vLabels = [wordFreqs[i][0]+" ("+ ('%s' % i) +")" for i in range(len(wordFreqs))]
	g.vs["label"] = vLabels

	# add edges
	num_edges=min(len(edgeList), E_NUM)
	for i in range(num_edges):
		g.add_edge(edgeList[i][0], edgeList[i][1])
	g.es["weight"]=[edgeList[i][2] for i in range(num_edges)]

	imgSize = round(pow(V_NUM, 0.85) * 40 + 2*100, -1)
	#math.ceil((math.log10(len(g.es))*700.0 + 100.0)/100.0)*80
	#layout=g.layout("grid_fr", area=(len(g.vs)**2), cellsize=imgSize, repulserad=1*(len(g.vs)**2.6))
	#layout = g.layout_reingold_tilford_circular()
	layout = g.layout_auto()



	# set visual style 
	visual_style = {}
	visual_style["vertex_size"] = 20
	
	maxDegree = g.maxdegree()
	visual_style["vertex_color"] = [(
		math.sqrt(1.0*g.degree(i)/maxDegree),
		0,
		1.0 - math.sqrt(1.0*g.degree(i)/maxDegree), 
		) for i in range(len(g.vs))]

	# calculate vertex size (function of degree)
	vertex_size = [40*math.log(1.0*g.degree(i)/maxDegree + 1.0) + 10.0 for i in range(len(g.vs))]
	visual_style["vertex_size"] = [vertex_size[i] for i in range(len(g.vs))]
	visual_style["vertex_label_dist"] = 0.75

	# edge weight calculation
	min_weight = min(g.es["weight"])
	MIN_WEIGHT = 1
	MAX_WEIGHT = 8
	edge_weight = [1.5*min(math.log(g.es["weight"][i]/min_weight) + MIN_WEIGHT, MAX_WEIGHT) for i in range(len(g.es))]
	visual_style["edge_width"] = edge_weight
	visual_style["edge_color"] = [ (
		(2.0*math.sqrt(1.0*edge_weight[i]/MAX_WEIGHT) + 1.0)/3.0,
		1.0/3.0,
		(2.0*(1.0 - math.sqrt(1.0*edge_weight[i]/MAX_WEIGHT)) + 1.0)/3.0
		) for i in range(len(g.es))]

	visual_style["layout"] = layout
	visual_style["bbox"] = (imgSize, imgSize)
	visual_style["margin"] = 100#0.5*vNum+100

	plot(g, labels=True, **visual_style)

	return #g, visual_style


def wordSim(wA, wB, basic=False):

	if wA.strip() == wB.strip():
		return 0.0

	raw = difflib.SequenceMatcher(a=wA.lower(), b=wB.lower()).ratio()

	if basic:
		return raw
	lA = len(wA)
	lB = len(wB)
	if lA == 0 or lB == 0: return 0
	lavg=pow(lA*lB, 0.5)
	score = pow(raw, 1.0 + 2.0/lavg)
	return score

def similarity(docA, docB, syns=False, weightType="importance"):

	return documentSimilarity(docA, docB, syns=syns, weightType=weightType)

def documentSimilarity(docA, docB, syns=False, weightType="importance"):
	uniqA = getWordFreqs(filter(docA, lemmatize=True, lemType=2))
	uniqB = getWordFreqs(filter(docB, lemmatize=True, lemType=2))

	''' 
	Algorithm:
	for each set of words:
		caluclate what percent are in the other document

	'''

	sim = 0

	fASum = 0
	fBSum = 0

	for itemA in uniqA:
		fASum += itemA[1]*itemA[1]
	for itemB in uniqB:
		fBSum += itemB[1]*itemB[1]

	if fASum == 0 and fBSum == 0:
		return 0

	# precompute synonyms
	Asyns=[]
	Bsyns=[]
	if syns==True:
		for word in uniqA:
			Asyns.append(synonyms(word[0]))
		for word in uniqB:
			Bsyns.append(synonyms(word[0]))

	Asyns = filter(Asyns, lemmatize=True, lemType=2)
	Bsyns = filter(Bsyns, lemmatize=True, lemType=2)

	matches=0

	#for itemA in uniqA:
	#	for itemB in uniqB:
	for i in range(len(uniqA)):
		itemA = uniqA[i]
		for j in range(len(uniqB)):
			itemB = uniqB[j]

			match = False
			if (syns == False):
				match = itemA[0] == itemB[0]
			else:
				
				if len(Bsyns[j]) == 0 or len(Asyns[i]) == 0:
					match = itemA[0] == itemB[0]
					#match = wordSim(itemA[0], itemB[0]) > 0.8
				else:
					'''
					AinB = itemA[0] in Bsyns[j]
					BinA = itemB[0] in Asyns[i]
					match = (AinB and BinA)# or wordSim(itemA[0], itemB[0]) > 0.8
					'''
					#match = wordsRelated(itemA[0], itemB[0])
					match = len(set(Asyns[i]) & set(Bsyns[j])) >= 1
				
			if match:
				matches += 1
				if QUIET == False:
					print "\tmatch: ",itemA[0], "(",itemB[0],")"
				fA = itemA[1]
				fB = itemB[1]

				if (weightType == "importance"):
					sim += fA*fB # / pow(fA* fB, 0.5)
				else:
					sim += fA + fB
				
				if (syns==False):
					break;

	if QUIET == False:
		print "matches: ", matches

	if (weightType == "importance"):
		return sim/(max(fASum, fBSum))
	else:
		return sim


def query(doc, query, syns=True):

	return queryDocument(doc, query, syns=syns)

def queryDocument(doc, query, syns=True, getScores=False, SCORE_SORT=True):

	# convert the query into a tiny document
	query = query.replace('.', '').replace('?', '')
	query = [query.split()]


	# find sentences in doc that match query
	matches=[]
	for sentence in doc:
		miniDoc = [sentence]
		simScore=documentSimilarity(miniDoc, query, syns=syns, weightType="sumWeights")
		#matches.append((sentence, documentSimilarity(miniDoc, query, syns=syns)))

		# if we are not sorting by score, then add all lines to output
		if simScore != 0 or not SCORE_SORT:
			matches.append((sentence, sf(simScore)))

	#sort matches
	if SCORE_SORT:
		matches.sort(key=lambda tup: tup[1])
		matches.reverse()

	if getScores:
		answers=[]
		for i in range(len(matches)):
			answers.append([' '.join(matches[i][0]), matches[i][1]])

		return answers
	else:
		answers=[]
		for i in range(len(matches)):
			answers.append(' '.join(matches[i][0]))

		return answers


def property(doc, prop, syns=True):

	return documentProperty(doc, prop, syns=syns)

def paintImage(doc):
	colours = [0]*11
	colours[0] = documentProperty(doc, "purple")
	colours[1] = documentProperty(doc, "bluish")
	colours[2] = documentProperty(doc, "greenish")
	colours[3] = documentProperty(doc, "yellowish")
	colours[4] = documentProperty(doc, "orange")
	colours[5] = documentProperty(doc, "reddish")
	colours[6] = documentProperty(doc, "blackness")
	colours[7] = documentProperty(doc, "whiteness")
	colours[8] = documentProperty(doc, "greyness")
	colours[9] = documentProperty(doc, "cyan")
	colours[10]= documentProperty(doc, "brown")

	(valence, arousal, dominance) = affectiveRatings(doc, normalized=True)
	VAD=(valence[1], arousal[1], dominance[1])

	painter.drawImage(VAD, colours)

def documentProperty(doc, prop, syns=True):
	#if len(prop.split()) != 1:
	#	print "ERROR: Property must be single word"
	#	return

	'''
	Algorithm 1:
		treat word list as document -> calculate document similarity with synonyms

	'''
	#propSyns=synonyms(prop)

	#if len(propSyns) == 0:
	#	return documentSimilarity(doc, [[prop]], syns=False)
	#else:
	#	return documentSimilarity(doc, [propSyns], syns=syns)
	return documentSimilarity(doc, [prop.split()], syns=syns)

def properties(docA):
	'''
	test the following:
		- colours
		- shape
		- size
		- good/bad
		- texture
	'''

	print "Colour"
	print "\tPurple: ", sf(documentProperty(docA, "purple"))
	print "\tBlue:   ", sf(documentProperty(docA, "bluish"))
	print "\tGreen:  ", sf(documentProperty(docA, "greenish"))
	print "\tYellow: ", sf(documentProperty(docA, "yellowish"))
	print "\tOrange: ", sf(documentProperty(docA, "orange"))
	print "\tRed:    ", sf(documentProperty(docA, "reddish"))
	print "\tBlack:  ", sf(documentProperty(docA, "blackness"))
	print "\tWhite:  ", sf(documentProperty(docA, "whiteness"))
	print
	print "Size"
	print "\tLarge:  ", sf(documentProperty(docA, "large ample"))
	print "\tSmall:  ", sf(documentProperty(docA, "small youthful little"))
	print
	print "Affective Ratings"
	(valence, arousal, dominance) = affectiveRatings(docA, normalized=True)
	avgV=5.06
	avgA=4.21
	avgD=5.18
	print "\tHappiness:  ", valence[1]
	print "\tExcitement: ", arousal[1]
	print "\tIn Control: ", dominance[1]


def affectiveRatings(doc, normalized=True):

	# ARATINGS=[ARwords, ARvalence, ARarousal, ARdominance]

	# load affective ratings data
	words=ARATINGS[0]
	valence=ARATINGS[1]
	arousal=ARATINGS[2]
	dominance=ARATINGS[3]

	# for each word in doc, find ratings
	wordFreqs=getWordFreqs(filter(doc))

	vSum = 0
	aSum = 0
	dSum = 0

	pts=0

	weightSum=0

	for w in wordFreqs:
		w1 = w[0]
		w2 = lemmatizer(w[0], lemType=1)

		wUsed=w[0]

		if w1 in words:
			wUsed = w1
		elif w2 in words:
			wUsed = w2
		else:
			continue
		
		# the word is in the VAD database...

		pts += 1

		#print w[0]+" in "+"words"

		weight=pow(w[1], 2.0)
		weightSum += weight

		index = words.index(wUsed)
		
		vSum += float(valence[index]) * weight
		aSum += float(arousal[index]) * weight
		dSum += float(dominance[index]) * weight

	if pts == 0:
		return [("valence", 0), ("arousal",0), ("dominance",0)]

	# weighted averages for the document
	vWAvg = vSum / weightSum
	aWAvg = aSum / weightSum
	dWAvg = dSum / weightSum

	# average/min/max of all the words in the database
	avgV=5.06
	minV=1.26
	maxV=8.48

	avgA=4.21
	minA=1.6
	maxA=7.79

	avgD=5.18
	minD=1.68
	maxD=7.74

	if not normalized:
		return [("valence", vWAvg), ("arousal",aWAvg), ("dominance",dWAvg)]
	else:
		# rescale the values to [-1, 1] with the average value going to 0
		normV = (vWAvg- avgV)/(maxV-avgV) if vWAvg>avgV else (avgV-vWAvg)/(minV-avgV)
		normA = (aWAvg- avgA)/(maxA-avgA) if aWAvg>avgA else (avgA-aWAvg)/(minA-avgA)
		normD = (dWAvg- avgD)/(maxD-avgD) if dWAvg>avgD else (avgD-dWAvg)/(minD-avgD)
		return [("valence", normV), ("arousal",normA), ("dominance",normD)]



def importantSentences(doc, SEN_NUM=20, CHRON=False, SCORE_SORT=True, DECAY_FACTOR=0.25):
	'''
	Algorithm 1:
		- get word frequencies
		- sort sentences by sum of word importantSentences
			- for each sentence, have tmpImportances and decrease
				importances for words already in sentence
			- also put a tiny amount of importance on important words
				being near front of sentence
			- put weight against sentence length
		- run through sorted sentences again with a tmpImportances
				list for all sentences
	'''
	# DECAY_FACTOR:
	# 	a term is less important in a sentence if it has already been seen in an important sentence,
	#	so make it a litte less important every time you see it

	filteredDoc=filter(doc, lemmatize=True, lemType=1)

	# unique non-stop words with frequencies
	wordFreqs=getWordFreqs(filteredDoc)
	words = [item[0] for item in wordFreqs]

	senScores=[]
	#for sentence in filtered:
	for i in range(len(filteredDoc)):
		sentence = filteredDoc[i]

		# create temporary word importance list
		tmpFreqs = copy.deepcopy(wordFreqs)

		score = 0
		senLen = len(sentence)
		for j in range(senLen):
			word = sentence[j]
			importance = tmpFreqs[words.index(word)][1]
			locFactor = 0.5 + 0.5/(1.0 + pow((i/30.0), 2.0))
			score += importance * locFactor
			# set future importance of word to 0
			tmpFreqs[words.index(word)] = (word, importance*0.25)

		score = score * 1.0/(1.0 + pow((senLen/40.0), 2.0))
		senScores.append((i, score)) # only store index of sentece in document
		#senScores.append((' '.join(doc[i]), score))
		#senScores.append((sentence, score))

	senScores.sort(key=lambda tup: tup[1])
	senScores.reverse()
	#return senScores[0:SEN_NUM]

	# sort sentences again -- giving ones at very top the advantage
	# this makes it so that we end up with a list of important sentences covering unique words
	newSenScores=[]

	tmpFreqs = copy.deepcopy(wordFreqs)
	for i in range(len(filteredDoc)):
		senIndex=senScores[i][0]
		sentence = filteredDoc[senIndex]

		score = 0
		senLen = len(sentence)
		for word in sentence:
			importance = tmpFreqs[words.index(word)][1]
			score += importance
			# multiply word importance by decay factor
			tmpFreqs[words.index(word)] = (word, importance*DECAY_FACTOR)
		score = score * 1.0/(1.0 + pow((senLen/40.0), 2.0))
		newSenScores.append((' '.join(doc[senIndex]), score, senIndex))
	

	
	newSenScores.sort(key=lambda tup: tup[1])
	newSenScores.reverse()
	newSenScores = newSenScores[0:SEN_NUM]


	if CHRON == True:
		newSenScores.sort(key=lambda tup: tup[2])
	

	#newSenScores = [(item[0], sf(item[1], 3)) for item in newSenScores]
	return newSenScores

def comparisonSummary(docA, docB):

	Afreqs=[item[0] for item in getWordFreqs(filter(docA, lemmatize=True))]
	Bfreqs=[item[0] for item in getWordFreqs(filter(docB, lemmatize=True))]

	print "==== Document Comparison Summary ===="
	print
	# calculate document similarity
	print "Similarity score:", documentSimilarity(docA, docB)
	print
	intersection=wordIntersection(docA, docB)
	print "Top words for doc 1:", Afreqs[0:5]
	print "Top words for doc 2:", Bfreqs[0:5]
	print
	Aadjs=adjectives(docA)
	Badjs=adjectives(docB)
	print "Top adjectives for doc 1:", Aadjs[0:5]
	print "Top adjectives for doc 2:", Badjs[0:5]
	print
	Anouns=nouns(docA)
	Bnouns=nouns(docB)
	print "Top nouns for doc 1:", Anouns[0:5]
	print "Top nouns for doc 2:", Bnouns[0:5]
	# find intersection of documents
	print
	print "Intersection of frequent words:"
	p(intersection[0:10])
	print "====================================="

def summary(doc, SEN_NUM=5, TYPE="short", CHRON=True):

	return documentSummary(doc, SEN_NUM=SEN_NUM, TYPE=TYPE, CHRON=CHRON)

def documentSummary(doc, SEN_NUM=5, TYPE="short", CHRON=True):
	'''
	Things to show:
		- top words
		- top adjectives
		- top nouns
		- top sentences
	'''

	print "Sentences:", len(doc)
	if len(doc) == 0: return
	print

	SEN_NUM = min(SEN_NUM, len(doc))

	IS=importantSentences(doc, SEN_NUM=SEN_NUM, CHRON=CHRON)
	if CHRON == False:
		print "Most important sentences"
		for i in range(SEN_NUM):
			print (i+1),": ",IS[i][0], "[",IS[i][2],"]"
	else:
		print "Document summarization"
		for i in range(SEN_NUM):
			print IS[i][0], "[",IS[i][2],"]"
	
	 

	freqs = getWordFreqs(filter(doc, lemmatize=True, lemType=1))
	if TYPE=="short":
		print "Top words: ", freqs[0][0], "(",sf(freqs[0][1],2),"), ",freqs[1][0], "(",sf(freqs[1][1],2),"), ",freqs[2][0], "(",sf(freqs[2][1],2),")"
	else:
		print "Top words:"
		p(freqs[0:6])
		print
		print "Top adjectives"
		p(adjectives(doc)[0:6])
		print
		print "Top nouns"
		p(nouns(doc)[0:6])


def adjectives(doc):
	# only get adjectives
	return wordTags(doc, POS="JJ")

def nouns(doc):
	# only get nouns
	return wordTags(doc, POS="NN")

def properNouns(string):
	tagged_sent = nltk.pos_tag(string.split())
	# [('Michael', 'NNP'), ('Jackson', 'NNP'), ('likes', 'VBZ'), ('to', 'TO'), ('eat', 'VB'), ('at', 'IN'), ('McDonalds', 'NNP')]

	propernouns = [word for word,pos in tagged_sent if pos == 'NNP']

	return propernouns


def wordTags(doc, POS="JJ"):
	'''
	Algorithm:
		- for each sentence in document:
			- find adjectives and add to list
		- filter stop words for adj list
		- sort adj list by frequency
		- return sorted list
	'''

	#filteredDoc=filter(doc, lemmatize=True, lemType=1)

	#stop=loadData("stopwords.txt")

	adjList=[]

	for sentence in doc:
		tags=tagSentence(sentence)

		for tag in tags:
			if POS in tag[1]: #tag[1] == "JJ":
				if cleanWord(tag[0]) not in STOP: adjList.append(lemmatizer(cleanWord(tag[0]), lemType=1))

	counter=collections.Counter(adjList)
	freqs = counter.values()
	words = counter.keys()

	combo=[(words[i], freqs[i]) for i in range(len(words))]
	combo.sort(key=lambda tup: tup[1])
	combo.reverse()

	return combo

def auxItems(doc, queryTerm=""):
	# find sentences with auxiliary verbs


	auxSet=['be', 'was', 'can', 'could', 'dare', 'do', 'have', 'may', 'might', 'must', 'need', 'ought', 'shall', 'should', 'will', 'would']

	filteredDoc = filter(doc, lemmatize=True, lemType=1, removeStops=False)
	retList = []
	aSum = 0
	for i in range(len(doc)):
		#if "be" in filteredDoc[i]:

		hasQuery = queryTerm=="" or queryTerm in filteredDoc[i]

		if bool(set(auxSet) & set(filteredDoc[i]))==True and hasQuery:
			#retList.append(sentence)
			retList.append((' '.join(doc[i]), len(filteredDoc[i])))
			aSum += 1

	print "PCT: ", 1.0*aSum/ len(doc)
	retList.sort(key=lambda tup: tup[1])
	return retList

def topicGraph(topicList, threshold=-1):
	'''
	Algorithm:
		- learn and store topics
		- for each pair of topics
			- calculate similarity score and top common wordSim
		- create graph
			- with vertices as topics
			- edges between topics with simScore >= threshold
			- label edges with top word(s)
	'''

	numTopics = len(topicList)
	docList=[]
	for topic in topicList:
		print "learning", topic
		docList.append(learn(topic))
	
	topWordLists = []
	for doc in docList:
		topWords = getWordFreqs(filter(doc))
		topWords = [topWords[i][0] for i in range(len(topWords))]
		topWordLists.append(topWords)

	# min sim score to add edge to graph = threshold
	autoThreshold = threshold == -1
	simList = []

	edgeList=[]
	comparisons = 0.5 * (numTopics * (numTopics-1.0))
	pos = 0
	for i in range(0, numTopics-1):
		for j in range(i+1, numTopics):
			pos += 1
			print sf(100.0*pos / comparisons,2),'%'
			#print "comparing", topicList[i], topicList[j]
			simScore = similarity(docList[i], docList[j])
			#print "simScore =", simScore
			IW = ""
			if simScore >= threshold:
				intersect = wordIntersection(docList[i], docList[j])
				intersect = [intersect[k][0] for k in range(len(intersect))]

				if topWordLists[i][0] in intersect:
					intersect.remove(topWordLists[i][0])
				if topWordLists[j][0] in intersect:
					intersect.remove(topWordLists[j][0])

				IW = intersect[0]+' & '+intersect[1]

				#print "intersection = ", IW
			edgeList.append([i, j, simScore, IW])
			if autoThreshold: simList.append(simScore)

	if autoThreshold:
		simList.sort()
		threshold = simList[int(len(simList)*0.6)]
		print "threshold = ",threshold


	''' CREATE GRAPH '''
	V_NUM = numTopics
	g=Graph()
	visual_style = {}
	g.es["weight"]=1.0 # make it a weighted edge graph

	# add vertices
	for i in range(numTopics):
		g.add_vertex(i)

	# add vertex labels
	#vLabels = [item[0] for item in wordFreqs]
	vLabels = [topicList[i] for i in range(numTopics)]
	g.vs["label"] = vLabels

	# add edges
	num_edges=0
	# calculate num edges
	newEdgeList = []
	for edge in edgeList:
		if edge[2] >= threshold:
			newEdgeList.append(edge)
	num_edges = len(newEdgeList)

	for i in range(num_edges):
		g.add_edge(newEdgeList[i][0], newEdgeList[i][1])
	g.es["weight"]=[newEdgeList[i][2] for i in range(num_edges)]
	# edge weight calculation
	min_weight = min(g.es["weight"])
	MIN_WEIGHT = 0.5
	MAX_WEIGHT = 6
	edge_weight = [min(g.es["weight"][i]/min_weight + MIN_WEIGHT, MAX_WEIGHT) for i in range(len(g.es))]
	visual_style["edge_width"] = edge_weight


	#eLabels = [newEdgeList[i][3]+' ('+'%s'%sf(newEdgeList[i][2],1)+')' for i in range(num_edges)]
	eLabels = [newEdgeList[i][3] for i in range(num_edges)]
	g.es["label"] = eLabels




	imgSize = round(pow(V_NUM, 0.85) * 100 + 2*100, -1)
	#math.ceil((math.log10(len(g.es))*700.0 + 100.0)/100.0)*80
	#layout=g.layout("grid_fr", area=(len(g.vs)**2), cellsize=imgSize, repulserad=1*(len(g.vs)**2.6))
	
	layout = g.layout_auto()
	#layout = g.layout_reingold_tilford_circular()

	# set visual style 
	
	visual_style["vertex_size"] = 20

	visual_style["vertex_label_dist"] = 0.75

	# generate edge colours
	e_colours = []
	for i in range(num_edges):
		clr = (random()*1.0, random()*1.0, random()*1.0)
		while sum(clr) > 1.5 or sum(clr)<0.25:
			clr = (random()*1.0, random()*1.0, random()*1.0)

		e_colours.append(clr)
	
	visual_style["edge_color"] = e_colours

	visual_style["edge_label_color"] = e_colours


	visual_style["layout"] = layout
	visual_style["bbox"] = (imgSize, imgSize)
	visual_style["margin"] = 100#0.5*vNum+100

	plot(g, labels=True, **visual_style)

	return g, visual_style

def generality(doc):
	# calculate generality factor
	# = amount of {all, most, some, type, of} in document

	indicators = ["all", "most", "some", "type", "general", "area"]#, "of"]

	filteredDoc = filter(doc, lemmatize=False, removeStops=False)

	gf = 0
	words = 0
	for sentence in filteredDoc:
		for word in sentence:
			words += 1
			if word in indicators:
				#print word
				gf += 1



	return 1.0*gf/words


''' DEMOS '''

def demo_list():
	print "demo_summary"
	print "demo_comparison"
	print "demo_paint"
	print "demo_properties"
	print "demo_query"
	print "demo_similarity"
	print "demo_web"
	print "demo_topicGraph"

def demo_summary():
	print "Getting summary of article on cats."
	summary(C)

def demo_comparison():
	# affective ratings
	# main sentences
	print "Comparing the articles on cats and dogs."
	comparisonSummary(C, D)
	return

def demo_properties():
	print "Finding properties in article on ocean."
	properties(O)
	return

def demo_paint():
	print "Generating images based on pumpkin and death articles."
	paintImage(PUMPKIN)
	paintImage(DEATH)
	return

def demo_query():
	print 'Querying article on Plato with "When did Plato die?"'
	query(P, "when did Plato die?")[0:5]
	return

def demo_similarity():
	print 'Calculating similarity between:'
	print '\t  dogs and      cats: ', similarity(A, B)
	print '\tapples and   bananas: ', similarity(D, C)
	print '\tPlato  and Aristotle: ', similarity(P, ARISTOTLE)
	print
	print '\t  cats and    apples: ', similarity(C, A)
	print '\t  dogs and     Plato: ', similarity(D, P)
	print '\t Plato and   bananas: ', similarity(P, B)
	return

def demo_web():
	print "Generating a word web about pumpkins"
	wordWeb(PUMPKIN)
	return

def demo_topicGraph():
	topicList=[]
	'''
	topicList.append("einstein")
	topicList.append("electricity")
	topicList.append("photons")
	topicList.append("world war 2")
	
	topicList.append("uranium")
	topicList.append("plutonium")
	topicList.append("radioactive")
	topicList.append("alan turing")
	topicList.append("microsoft")
	topicList.append("google")
	'''
	
	
	topicList.append("nikola tesla")
	topicList.append("einstein")
	topicList.append("niels bohr")
	topicList.append("richard feynman")
	topicList.append("marie curie")
	topicList.append("isaac newton")
	topicList.append("enrico fermi")
	
	
	

	
	g, visual_style = topicGraph(topicList, threshold = 0)

	return g, visual_style

def demo_generality():
	SCIENCE = learn("science")
	MATH = learn("mathematics")
	BIO = learn("biology")
	PHYSICS =learn("physics")
	FRUIT = learn("fruit")
	ANIMAL = learn("animal")

	print "ANIMAL", generality(ANIMAL)
	print "\tCAT", generality(C)
	print "\tDOG", generality(D)
	print "SCIENCE", generality(SCIENCE)
	print "\tMATH", generality(MATH)
	print "\tBIO", generality(BIO)
	print "\tPHYS", generality(PHYSICS)
	print "FRUIT", generality(FRUIT)
	print "\tAPPLE", generality(A)
	print "\tBANANA", generality(B)




#print "Loaded KnowledgeTools. Type help() for function list.\n"

#print "Apples(A), Bananas(B), Cats(C), Dogs(D), Plato(P)"

STOP=loadData("/home/tanner/Dropbox/sandbox/FermiV9/Code/KnowledgeTools/Code/stopwords.txt")

tmp = lemmatizer("cats", 1) # initialize the lemmatizer
tmp = lemmatizer("cats", 0)

ARwords=[]
ARvalence=[]
ARarousal=[]
ARdominance=[]

with open('/home/tanner/Dropbox/sandbox/FermiV9/Code/KnowledgeTools/Code/AffectiveRatings.txt','r') as f:
	next(f) # skip headings
	reader=csv.reader(f,delimiter='\t')
	for w, v, a, d in reader:
		#print w, v, a, d
		ARwords.append(w)
		ARvalence.append(float(v)) 
		ARarousal.append(float(a))
		ARdominance.append(float(d))

ARATINGS=[ARwords, ARvalence, ARarousal, ARdominance]
