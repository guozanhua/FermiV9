import subprocess
import datetime, time
import sys
import fileinput
from random import randint
import difflib		# for string similarity
import copy
import re # for regular expression stuff
import math
import threading# to check time since last command every x minutes

import urllib2
from bs4 import BeautifulSoup
import signal # for watching for timeouts from web scrapes

#import Tkinter as tk # for clipboard copying
from Tkinter import *
# apt-get install python-imaging-tk
import PIL.Image
from PIL import ImageTk

DIR = '/home/tanner/Dropbox/sandbox/FermiGit/V9/'
KTDIR = DIR+'Code/KnowledgeTools/Code/'

sys.path.insert(0, KTDIR)
from kt2 import timeout
from kt2 import TimedOutExc
import kt2 as k

import monologue as m
from fileIO import *
from phraseModify import *
import aasr
#import question_lib.aasr as aasr
from patterns_lib.patternMatching import *
from patterns_lib.recursiveMatching import *


DATA_DIR=DIR+'Database/'
SETS_DIR=DIR+'Settings/'

QV = m.loadVecList('../VecLists/quotes_1.txt')

GLOB = {'CMDS': [],							# load
		'CMDE': [],							# load
		'CMDHIST': [],						# yaml
		'MOOD' : [],
		'PREVMOOD' : [],
		'MOODDIM' : 12,
		'EMOTIONS' : [],					# load
		'SETTINGS' : [],					# load
		'INGESTED' : [],					# yaml
		'CHATDATA' : [],					# load
		'CORRECTIONS' : [],					# load
		'onQuery' : False,
		'curFace' : "neutral",
		'remindersSent' : 0,
		'prevUsageTime' : time.time(),
		'CONTEXT' : "",
		'contextLocked': True,
		'FEATURES' : [],
		'FACTUAL_MEMORY' : {},				# json
		'AUTOBIOGRAPHIC_MEMORY' : [],			# json
		'SEND_TEXT' : False}



WIDTH = 1366/2
HEIGHT = 768/2

tk_BGC = "black"
tk_TXC = "white"

tk_FermiBlue = "#%02x%02x%02x" % (66, 107, 255)
tk_FermiDarkBlue = "#%02x%02x%02x" % (32, 55, 133)

tk_root = Tk()
tk_root.geometry("%dx%d%+d%+d" % (WIDTH, HEIGHT, WIDTH/2, HEIGHT/2))
tk_root.title("Fermi V9")
tk_root.configure(background=tk_BGC)

icon_img = ImageTk.PhotoImage(file=DATA_DIR+'fermi-icon.png')
tk_root.tk.call('wm', 'iconphoto', tk_root._w, icon_img)

tk_user_input = Text(tk_root, width=25, height=3, bd=0,
				highlightthickness=0, wrap="word", font=("monospace", 10),
				background=tk_TXC, fg=tk_BGC, insertbackground=tk_BGC)

tk_history = Text(tk_root, width=25, height=6, fg=tk_TXC, background=tk_BGC,
				bd=0, highlightthickness=0, wrap="word", font=("monospace", 10))

tk_side = Text(tk_root, width=25, height=6, fg=tk_FermiBlue, background=tk_BGC, bd=0, highlightthickness=0)

tk_top = Text(tk_root, width=25, height=6, fg=tk_FermiBlue, background=tk_BGC, bd=0, highlightthickness=0, wrap="word")

tk_CC = Canvas(tk_root, width=100, height=100, background=tk_BGC, bd=0, highlightthickness=0)

fp = open(DATA_DIR+'faces_blue/intro_animation/intro_0.png',"rb")
original = PIL.Image.open(fp)
resized = original.resize((100, 100),PIL.Image.ANTIALIAS)
image = ImageTk.PhotoImage(resized)
tk_face = Label(tk_root, image=image, background=tk_BGC)
fp.close()

