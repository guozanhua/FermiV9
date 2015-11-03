from header import *
import tkSimpleDialog
import tkMessageBox

FRAME_NUM= 0
FRAME_DT = 0.25

PAUSE_ANIM=False

C_DIR = DATA_DIR+"concentric_circles/"
C_NUM = 7

imagelist=[]
CL=[]
CL2=[]
baseC=[]
CCAngles = [0 for i in range(C_NUM)]

TAGGED_HIST_LINES=[]
H_CLEARS = 0

def initCC(anim=False):

	global imagelist, CL, C_NUM, C_DIR, baseC
	global tk_BGC

	#from common import setting
	#CS = setting("COLOUR_SCHEME")

	orig = PIL.Image.open(open(C_DIR+"c_all_blue.png","rb"))
	resized = orig.resize((100, 100),PIL.Image.ANTIALIAS)
	baseC = ImageTk.PhotoImage(resized)
	tk_CC.create_image(50, 50, image=baseC, tags="base")

	for i in range(C_NUM):
		imagelist.append(C_DIR+"cover_"+tk_BGC+"/d_"+'%s.png'%i)
	# create list of images overlap
	for img in imagelist:
		orig = PIL.Image.open(open(img,"rb"))
		resized = orig.resize((100, 100),PIL.Image.ANTIALIAS)
		new_photo = ImageTk.PhotoImage(resized)
		CL.append(new_photo)
		
		CL2.append(resized)



	# now place images on canvas
	index=0
	for img in CL:
		tk_CC.create_image(50, 50, image=img, tags="c"+'%s'%index)
		tk_CC.update()
		if anim:
			rotateCircle(index, angle=(180/C_NUM)*index, autoDirection=False)
			time.sleep(0.05)
		index += 1

	tk_root.update()


# to create new colours, got to a folder and do:
# for a in *.png; do convert -modulate 100,100,-25 "$a" "$a"; done

def writeToLocation(inStr, location, PAUSE_SEND=False):
	if location == "history":
		tkHistCat(inStr, PAUSE_SEND=PAUSE_SEND)
	elif location == "top":
		#tkTopClear()
		tkTopCat(inStr)

def tkHistClear():
	global TAGGED_HIST_LINES, H_CLEARS
	TAGGED_HIST_LINES = []
	H_CLEARS += 1

	tk_history.configure(state='normal')

	tk_history.delete("1.0", END)
	tk_history.update()

	tk_history.configure(state='disabled')

	tk_root.update()
	
	return

def tkHistCat(inStr, PAUSE_SEND=False):
	from reminders import sendText

	if GLOB['SEND_TEXT'] and inStr.strip().find('>>') != 0 and not PAUSE_SEND:
		txtStr = inStr.strip()
		#if txtStr.find('>>') == 0:
		#	txtStr = txtStr[3:]
		sendText(txtStr)

		GLOB['SEND_TEXT'] = False
		tkTopCat("*Text sent*")

	tk_history.configure(state='normal')

	tk_history.insert(END, inStr)

	LINES = copy.deepcopy(tk_history.get('1.0', 'end-1c').splitlines())

	if len(LINES) >= 75:
		tkHistClear()

		toReAdd = ""
		for line in LINES[len(LINES)-25:]:

			toReAdd += line+'\n'
		tkHistCat(toReAdd)
		tk_history.configure(state='disabled')
		return
	
	tk_history.yview(END)
	tk_history.configure(state='disabled')

	tkHistColour()

	tk_root.update()


def tkHistColour(resetHist=False):
	global TAGGED_HIST_LINES, H_CLEARS

	global tk_BGC, tk_TXC

	from common import setting
	from phraseModify import split2
	CS = setting("COLOUR_SCHEME")

	pos=1

	LINES = tk_history.get('1.0', 'end-1c').splitlines()

	for l in range(len(LINES)):
		line = LINES[l]

		
		if line+'%s %s'%(l, H_CLEARS) in TAGGED_HIST_LINES:
			pos += 1
			continue
		else:
			TAGGED_HIST_LINES.append(line+'%s %s'%(l, H_CLEARS))
		
		
	
		if line.strip() == "":
			pos += 1
			continue

		# Iterate lines
		#print "->", line


		if line[0:2] == ">>":
			# it's from user

			if setting("VAD_COLOURING"):
				words = split2(line)
				for W in words:
					word = W[0]
					wStart = W[1]
					wEnd = W[2]

					C = '#%02x%02x%02x'%wordToRGB(word)
					tagName='%s.%s'%(pos,wStart)+'F-VAD'+'%s'%H_CLEARS
				
					tk_history.tag_add(tagName, '%s.%s'%(pos,wStart), '%s.%s'%(pos, wEnd))
					tk_history.tag_config(tagName, background=tk_BGC, foreground=C)
			

			tagNameU='%s.2'%pos+'U'+'%s'%H_CLEARS
			
			tk_history.tag_add(tagNameU, '%s.0'%pos, '%s.2'%pos)
			if CS != "blue":
				tk_history.tag_config(tagNameU, background=tk_BGC, foreground=CS, font=("monospace", "10", "bold"))
			else:
				tk_history.tag_config(tagNameU, background=tk_BGC, foreground=tk_FermiBlue, font=("monospace", "10", "bold"))
		else:

			tagName='%s.0'%pos+'%s'%H_CLEARS
			
			tk_history.tag_add(tagName, '%s.0'%pos, END)
			tk_history.tag_config(tagName, background=tk_BGC, foreground=tk_TXC)	

			if setting("VAD_COLOURING"):
				words = split2(line)
				for W in words:
					word = W[0]
					wStart = W[1]
					wEnd = W[2]

					C = '#%02x%02x%02x'%wordToRGB(word)
					tagName='%s.%s'%(pos,wStart)+'F-VAD'+'%s'%H_CLEARS
					
					tk_history.tag_add(tagName, '%s.%s'%(pos,wStart), '%s.%s'%(pos, wEnd))
					tk_history.tag_config(tagName, background=tk_BGC, foreground=C)
			



			locLS = line.find('[')
			locRS = line.find(']')
			if locLS==0 and locRS != -1:

				tagNameF='%s.0'%pos+'F'+'%s'%H_CLEARS
		
				tk_history.tag_add(tagNameF, '%s.0'%pos, '%s.%s'%(pos, locRS+1))
				if CS != "blue":
					tk_history.tag_config(tagNameF, background=tk_BGC, foreground=CS, font=("monospace", "10", "bold"))
				else:
					tk_history.tag_config(tagNameF, background=tk_BGC, foreground=tk_FermiBlue, font=("monospace", "10", "bold"))
		

		pos += 1		


	tk_root.update()

	return

def VADtoRGB(V, A, D):
	from common import linTrans
	Vv = [1.0, 1.0, -1.0]
	Av = [1.0, -0.5, -1.0]
	Dv = [1.0, 1.0, 1.0]

	C = [0, 0, 0]
	C[0] = Vv[0]*V + Av[0]*A + Dv[0]*D
	C[1] = Vv[1]*V + Av[1]*A + Dv[1]*D
	C[2] = Vv[2]*V + Av[2]*A + Dv[2]*D

	maxC = max(max([abs(c) for c in C]), 1.0)
	C = [c/maxC for c in C]

	#C = [RED, GREEN, BLUE] # just get the value

	if C == [0, 0, 0]:
		#C = [0.75, 0.75, 0.75]
		if tk_BGC == "black":
			C = [1, 1, 1]
		else:
			C = [-0.75, -0.75, -0.75]

	C = [int(linTrans(c, [(-1, 0), (1, 255)])) for c in C]

	return C

def wordToRGB(word):
	from common import linTrans

	VAD = k.affectiveRatings([word.strip().split()], normalized=True)

	V, A, D = VAD[0][1], VAD[1][1], VAD[2][1]
	# happiness, arousal, control
	# = green    = red    = blue

	#RED = math.copysign(math.sqrt(abs(D)), D)
	#GREEN = math.copysign(math.sqrt(abs(A)), A)
	#BLUE = math.copysign(math.sqrt(abs(D)), D)

	#RED = A
	#GREEN = V
	#BLUE = D

	'''
	Vv = [1.0, 1.0, -1.0]
	Av = [1.0, -0.5, -1.0]
	Dv = [1.0, 1.0, 1.0]

	C = [0, 0, 0]
	C[0] = Vv[0]*V + Av[0]*A + Dv[0]*D
	C[1] = Vv[1]*V + Av[1]*A + Dv[1]*D
	C[2] = Vv[2]*V + Av[2]*A + Dv[2]*D

	maxC = max(max([abs(c) for c in C]), 1.0)
	C = [c/maxC for c in C]

	#C = [RED, GREEN, BLUE] # just get the value

	if C == [0, 0, 0]:
		#C = [0.75, 0.75, 0.75]
		if tk_BGC == "black":
			C = [1, 1, 1]
		else:
			C = [-0.75, -0.75, -0.75]

	C = [int(linTrans(c, [(-1, 0), (1, 255)])) for c in C]
	'''
	C = VADtoRGB(V, A, D)

	if tk_BGC == "black":
		C = [(3.0*c+1.0*255)/4.0 for c in C]
	else:
		C = [(2.0*c+1.0*0)/3.0 for c in C]

	return tuple(C)


def tkTopClear():
	
	tk_top.configure(state='normal')
	tk_top.delete("0.0", END)
	tk_top.configure(state='disabled')
	tk_root.update()
	
	return

def tkTopCat(inStr):
	tk_top.configure(state='normal')
	tk_top.insert(END, inStr.strip()+'\n\n')

	tk_top.yview(END)
	tk_top.configure(state='disabled')
	tk_root.update()



def tkSideClear():
	
	tk_side.configure(state='normal')
	tk_side.delete("0.0", END)
	tk_side.configure(state='disabled')
	tk_root.update()
	
	return

def tkSideCat(inStr):
	tk_side.configure(state='normal')
	tk_side.insert(END, inStr)

	tk_side.yview(END)
	tk_side.configure(state='disabled')
	tk_root.update()



def resizeLayout(event=[]):
	from common import setting

	LINEH = 17.0


	bf = 5 # buffer size in pixels
	bfo = 5 # for overriding a bf of 0

	pixelX=tk_root.winfo_width()
	pixelY=tk_root.winfo_height()
	
	# update user input
	inputW = 0
	if setting("MINIMAL_GUI"):
		inputW = pixelX
		bf = 0
	else:
		inputW = int(2.0*pixelX/3.0)
		

	inputH = int(3.0*LINEH)
	tk_user_input.place(x=bf, y=pixelY-inputH, width = inputW, height = inputH-bf)

	# update face
	faceW = 100
	faceH = 100
	tk_face.place(x=0, y=0, width=faceW, height=faceH)

	# update history
	histW = inputW
	histH = pixelY-inputH-faceH
	tk_history.place(x=bfo, y=faceH+bf, width = histW-bfo, height = histH-bf)

	# update top
	topW = histW- faceW - 100 - bfo
	topH = faceH
	tk_top.place(x=faceW, y=bfo, width = topW-bf, height = topH-bfo)


	
	if setting("MINIMAL_GUI"):
		tk_side.place_forget()
		#tk_CC.place_forget()

		# update concentric circles
		ccW = 100
		ccH = 100
		tk_CC.place(x=pixelX-100-bfo, y=0, width = ccW, height=ccH)

	else:
		# update side
		sideW = pixelX - histW
		sideH = pixelY-faceH
		tk_side.place(x=histW, y=faceH+bf, width = sideW-bf, height=sideH-bf)

		# update concentric circles
		ccW = 100
		ccH = 100
		tk_CC.place(x=pixelX-sideW/2-50, y=0, width = ccW, height=ccH)


	
def updateColour():
	global baseC
	from common import setting
	CS = setting("COLOUR_SCHEME")

	newColour = "blue"
	if CS != "blue":
		newColour = CS
	else:
		newColour = tk_FermiBlue

	tk_side.configure(fg=newColour)

	tk_top.configure(fg=newColour)

	tk_CC.delete("base")
	orig = PIL.Image.open(open(C_DIR+"c_all_"+CS+".png","rgba"))
	resized = orig.resize((100, 100),PIL.Image.ANTIALIAS)
	baseC = ImageTk.PhotoImage(resized)
	tk_CC.create_image(50, 50, image=baseC, tags="base")
	tk_CC.update()




def exitEvent():
	# save history
	yamlSave(GLOB['CMDHIST'], DATA_DIR+'history.txt')
	yamlSave(GLOB['INGESTED'], DATA_DIR+'ingested.txt')

	
	time.sleep(0.5)
	tk_root.quit()

def questionBox(qStr=""):
	result = tkSimpleDialog.askstring("Fermi", qStr)
	#if 'yes':
	#    print "Deleted"
	#else:
	#    print "I'm Not Deleted Yet"
	return result

def yesNoBox(qStr=""):
	result = tkMessageBox.askquestion("Fermi", qStr)
	if 'yes':
		return True
	else:
		return False

def facesDemo():
	from common import setting
	# show all basic emotions

	global PAUSE_ANIM
	PAUSE_ANIM = True
	for e in GLOB['EMOTIONS']:
		eName = e[2]

		fileName = eName+".png"

		fp = open(DATA_DIR+"faces_"+setting("COLOUR_SCHEME")+"/basic_emotions/"+fileName,"rb")
		original = PIL.Image.open(fp)
		resized = original.resize((100, 100),PIL.Image.ANTIALIAS)
		image = ImageTk.PhotoImage(resized)
		tk_face.configure(image=image)#, background="black")
		tk_face.image=image
		tk_root.update()

		tkTopCat('*'+eName+'*\n')

		rotateCircle(2, angle=45)

		time.sleep(0.5)

	tkTopCat('*confusion*\n')
	confusedAnimation()

	tkTopCat('*eye roll*\n')
	eyeRollAnimation()

	tkTopCat('*intro animation*\n')
	introAnimation()


	PAUSE_ANIM = False

	setFace(face=GLOB['curFace'])



	return

def setFace(face="blinking_animation", holdLook=0.5):
	from common import setting

	global FRAME_NUM

	fileName=""


	if face == "thinking_animation":
		FRAME_NUM=0
		thinkingAnimation()
		return
	elif face == "blinking_animation":
		blinkingAnimation()
		return
	elif face == "eye-roll_animation":
		eyeRollAnimation()
		return
	elif face == "look-up_animation":
		lookAnimation("up", holdLook=holdLook)
		return
	elif face == "look-left_animation":
		lookAnimation("left", holdLook=holdLook)
		return
	elif face == "look-right_animation":
		lookAnimation("right", holdLook=holdLook)
		return
	else:
		FRAME_NUM=float('inf')
		fileName = face+".png"

	try:

		fp = open(DATA_DIR+"faces_"+setting("COLOUR_SCHEME")+"/basic_emotions/"+fileName,"rb")
		#fp = open("hal.gif","rb")
		original = PIL.Image.open(fp)
		resized = original.resize((100, 100),PIL.Image.ANTIALIAS)
		image = ImageTk.PhotoImage(resized)
		tk_face.configure(image=image)#, background="black")
		tk_face.image=image
		tk_root.update()
		GLOB['curFace']=face
	except:
		print "ERROR: Face file not found:", face

def memoryAnimation(mood="positive"):
	from common import setting

	fileName="positive"
	if mood.lower() in ["happy", "positive"]:
		fileName = "positive.png"
	else:
		fileName = "negative.png"

	fp = open(DATA_DIR+"faces_"+setting("COLOUR_SCHEME")+"/memory_faces/"+fileName,"rb")
	original = PIL.Image.open(fp)
	resized = original.resize((100, 100),PIL.Image.ANTIALIAS)
	image = ImageTk.PhotoImage(resized)
	tk_face.configure(image=image)#, background="black")
	tk_face.image=image
	tk_root.update()
	time.sleep(0.5)

	setFace(face=GLOB['curFace'])

	return	

def thinkingAnimation():
	from common import setting
	global FRAME_NUM
	maxFrame=2

	#print args

	if FRAME_NUM > maxFrame:
		FRAME_NUM = 0
		return

	fileName="thinking_"+'%s'%FRAME_NUM+'.png'
	fp = open(DATA_DIR+"faces_"+setting("COLOUR_SCHEME")+"/thinking_animation/"+fileName,"rb")
	original = PIL.Image.open(fp)
	resized = original.resize((100, 100),PIL.Image.ANTIALIAS)
	image = ImageTk.PhotoImage(resized)
	tk_face.configure(image=image)#, background="black")
	tk_face.image=image

	FRAME_NUM += 1
	tk_root.update()
	if FRAME_NUM > maxFrame:
		FRAME_NUM = 0
		return

	t = threading.Timer(FRAME_DT, thinkingAnimation)
	t.daemon = True
	t.start()

def blinkingAnimation(holdLook=0.1, moveDt=0.01, mood=[]):
	if PAUSE_ANIM:
		return

	from common import setting
	if mood != []:
		mE = mood[1]
		# on scales from -1 to 1
		if mE <= -0.75:
			moveDt = 0.05
			holdLook = 0.75
		elif mE <= -0.5:
			moveDt = 0.03
			holdLook = 0.5
		elif mE <= 0.0:
			moveDt = 0.02
			holdLook = 0.3
		elif mE <= 0.5:
			moveDt = 0.01
			holdLook = 0.1
		else:
			moveDt = 0.005
			holdLook = 0.1
		holdLook = moveDt*10.0

	frames    = [0, 1, 2, 3, 4, 3, 2, 1, 0]
	# opening takes slightly longer than closing
	durations = [moveDt,
				moveDt,
				moveDt,
				moveDt,
				holdLook,
				moveDt*3.0,
				moveDt*3.0,
				moveDt*3.0,
				moveDt*3.0] 
	for f, d in zip(frames, durations):
	
		fileName="blinking_"+'%s'%f+'.png'
		fp = open(DATA_DIR+"faces_"+setting("COLOUR_SCHEME")+"/blinking_animation/"+fileName,"rb")
		original = PIL.Image.open(fp)
		resized = original.resize((100, 100),PIL.Image.ANTIALIAS)
		image = ImageTk.PhotoImage(resized)
		tk_face.configure(image=image)#, background="black")
		tk_face.image=image
		tk_root.update()
		time.sleep(d)

	setFace(face=GLOB['curFace'])

	return

def lookAnimation(direction="", holdLook=0.5, moveDt=0.1):
	from common import setting

	if PAUSE_ANIM: return

	if direction == "":
		R = randint(0, 2)
		if R == 0:
			direction = "up"
		elif R == 1:
			direction = "left"
		else:
			direction = "right"

	frames    = [0, 1, 2, 1, 0]
	durations = [moveDt, moveDt, holdLook, moveDt, moveDt] 


	for f, d in zip(frames, durations):
		fileName="look-"+direction+"_"+'%s'%f+'.png'
		fp = open(DATA_DIR+"faces_"+setting("COLOUR_SCHEME")+"/look-"+direction+"_animation/"+fileName,"rb")
		original = PIL.Image.open(fp)
		resized = original.resize((100, 100),PIL.Image.ANTIALIAS)
		image = ImageTk.PhotoImage(resized)
		tk_face.configure(image=image)#, background="black")
		tk_face.image=image
		tk_root.update()
		time.sleep(d)

	setFace(face=GLOB['curFace'])

	return

def eyeRollAnimation():
	from common import setting
	frames    = [0, 1, 2, 3, 4, 5, 6]
	# opening takes slightly longer than closing
	durations = [0.05, 0.1, 0.15, 0.15, 0.1, 0.05] 
	for f, d in zip(frames, durations):
	
		fileName="eye-roll_"+'%s'%f+'.png'
		fp = open(DATA_DIR+"faces_"+setting("COLOUR_SCHEME")+"/eye-roll_animation/"+fileName,"rb")
		original = PIL.Image.open(fp)
		resized = original.resize((100, 100),PIL.Image.ANTIALIAS)
		image = ImageTk.PhotoImage(resized)
		tk_face.configure(image=image)#, background="black")
		tk_face.image=image
		tk_root.update()
		time.sleep(d)

	setFace(face=GLOB['curFace'])

	return

def confusedAnimation():
	from common import setting
	frames    = [0, 1, 2, 1, 0]
	# opening takes slightly longer than closing
	durations = [0.1, 0.1, 0.5, 0.1, 0.2] 
	for f, d in zip(frames, durations):
	
		fileName="confused_"+'%s'%f+'.png'
		fp = open(DATA_DIR+"faces_"+setting("COLOUR_SCHEME")+"/confused_animation/"+fileName,"rb")
		original = PIL.Image.open(fp)
		resized = original.resize((100, 100),PIL.Image.ANTIALIAS)
		image = ImageTk.PhotoImage(resized)
		tk_face.configure(image=image)
		tk_face.image=image
		tk_root.update()
		time.sleep(d)

	setFace(face=GLOB['curFace'])

	return

def introAnimation():
	from common import setting
	frames    = range(12)
	# opening takes slightly longer than closing
	durations =[0.03,
				0.03,
				0.02,
				0.01,
				0.01,
				0.05,
				0.04,
				0.02,
				0.01,
				0.01,
				0.01,
				0.05]

	durations = [1.5*d for d in durations]

	for f, d in zip(frames, durations):
	
		fileName="intro_"+'%s'%f+'.png'
		fp = open(DATA_DIR+"faces_"+setting("COLOUR_SCHEME")+"/intro_animation/"+fileName,"rb")
		original = PIL.Image.open(fp)
		resized = original.resize((100, 100),PIL.Image.ANTIALIAS)
		image = ImageTk.PhotoImage(resized)
		tk_face.configure(image=image)#, background="black")
		tk_face.image=image
		tk_root.update()
		time.sleep(d)

	setFace(face=GLOB['curFace'])

	return

def introCCAnimation():

	global CL, CL2, CCAngles

	# now place images on canvas
	#elapsed_time = time.time() - GLOB['prevUsageTime']
	
	for t in range(0, 100):
		for i in range(len(CL2)):
			angle = i+1#(5*(C_NUM-i))#randint(1, 4)*5
			rotateCircle(index=i, angle=angle, autoDirection=False)

		time.sleep(0.01)





def ccRotateAnimation():
	from common import linTrans

	global CL, CL2, CCAngles
	

	# now place images on canvas
	#elapsed_time = time.time() - GLOB['prevUsageTime']
	
	energy = GLOB['MOOD'][1]

	for i in range(len(CL2)):
		if random() > 0.75:
			
			angle = linTrans(energy, [(-1, 5), (1, 15)]) #*(i+1)#randint(1, 4)*5
			rotateCircle(index=i, angle=angle)


	t = threading.Timer(linTrans(energy, [(-1, 1.5), (1, 0.5)]), ccRotateAnimation)
	t.daemon = True
	t.start()


def rotateCircle(index, angle, autoDirection=True):

	global CL, CL2, CCAngles

	if CL == []: return

	# delete specified circle
	cTag = "c"+'%s'%index
	tk_CC.delete(cTag)

	if autoDirection:
		if index%2 == 0:
			angle = -1*abs(angle)
		else:
			angle = abs(angle)


	CCAngles[index] = (CCAngles[index] + angle)%360
	CL[index] = ImageTk.PhotoImage(CL2[index].rotate(CCAngles[index]))
	tk_CC.create_image(50, 50, image=CL[index], tags=cTag)

	tk_root.update()
