import PIL
from PIL import Image
import ImageFilter
import copy


COLOURS=[(128, 0, 128), # purple
		(0, 0, 255), # blue
		(0, 255, 0), # green
		(255, 255, 0), #yellow
		(255, 165, 0), #orange
		(255, 0, 0), # red
		(0, 0, 0), # black
		(255, 255, 255), # white
		(128, 128, 128), # grey
		(0, 255, 255), # cyan
		(150, 75, 0) # brown
		]


def nest(img):
	# put smalles copies in it

	img2 = img.resize((int(img.size[0]*0.5), int(img.size[1]*0.5)))
	img3=img.copy()
	img3.paste(img2, (0, 0))
	img3.paste(img2, (int(img.size[0]*0.5), 0))
	img3.paste(img2, (0, int(img.size[1]*0.5)))
	img3.paste(img2, (int(img.size[0]*0.5), int(img.size[1]*0.5)))

	img4=img.copy()

	img = img.blend(img4, img3, 0.5)

	return img

def symmetric(img):
	img2=img.rotate(180)
	img2 = img2.resize((int(img2.size[0]*0.5), img2.size[1]))
	img.paste(img2, (0,0))

	img2 = img2.rotate(180)
	img.paste(img2, (int(img.size[0]*0.5), 0))

	return img
	

def drawImage(VAD, cReps, colours=COLOURS, ):
	'''
	VAD: VAD vector (3-tuple)
	cReps: amount of each colour to use
	colours: the actual colour definitions
	'''

	imgSize=(400, 200)

	img = Image.new( 'RGB', imgSize, "black") # create a new black image
	pixels = img.load() # create the pixel map

	'''
	Algorithm:
		- split up img into bars of colours (by proportion)
		- apply light/dark
		- apply blur

	'''

	cRepMod = cReps#[pow(cReps[i],2.0) for i in range(len(cReps))]

	# normalize colour rep vector
	if sum(cRepMod) == 0:
		pcr=[0]*len(cRepMod)
	else:
		pcr = [1.0*cRepMod[i]/sum(cRepMod) for i in range(len(cRepMod))]

	combo=[(colours[i], pcr[i]) for i in range(len(colours))]
	combo.sort(key=lambda tup: tup[1])
	combo.reverse()

	colours = [combo[i][0] for i in range(len(colours))]
	pcr = [combo[i][1] for i in range(len(pcr))]

	# X: img.size[0]
	# Y: img.size[1]
	#
	# o ===> +x
	# |
	# v
	# +y

	xDist=0
	for i in range(len(pcr)):
		if pcr == [0]*len(cRepMod):
			for x in range(img.size[0]):
				for y in range(img.size[1]):
					pixels[x,y] = (0,0,0)
		else:
			for x in range(xDist, min(xDist+int(img.size[0]*pcr[i]), img.size[0])):
				xDist += 1
				for y in range(img.size[1]):
					pixels[x,y] = colours[i]


	''' APPLY BRIGHTNESS '''
	# 0: black, 0.5: normal, 1.0: white
	B = 0.5*(VAD[0]*0.75 + 1.0)
	for x in range(img.size[0]):
		for y in range(img.size[1]):
			curClr = pixels[x,y]

			if B > 0.5:
				Bp = (B - 0.5)*2.0
				newClr = [int(curClr[i]*(1.0-Bp) + Bp*255) for i in [0,1,2]]
			else:
				Bp = B*2.0
				newClr = [int(curClr[i]*Bp) for i in [0,1,2]]

			pixels[x,y] = tuple(newClr)

	''' APPLY BLUR '''
	blurAmount = 0
	for i in range(blurAmount):
		img = img.filter(ImageFilter.SMOOTH_MORE)

	
	img = symmetric(img)
	#img = nest(img)
	#img.save('test2.png')
	
	img.show()


if __name__ == "__main__":

	'''
	Happiness:   0.416650586067
	Excitement:  -0.20061265048
	In Control:  0.186244212667
	'''

	VAD=(0.4, -0.2, 0.18)
	cReps =[5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5]
	drawImage(VAD, cReps)