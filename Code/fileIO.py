import json
import yaml


def jsonSave(data, fileName, indent=True, sort=False, oneLine=False):
	f = open(fileName, 'w')


	if indent:
		f.write(json.dumps(data, indent=4, sort_keys=sort))
	else:
		f.write(json.dumps(data, sort_keys=sort))

	f.close()

def jsonLoad(fileName):
	try:
		file = open(fileName)
		t=file.read()
		file.close()
		return json.loads(t)
	except:
		return {}

def yamlLoad(fileName, maxLen=-1):
	try:

		stream = file(fileName, 'r')
		R = yaml.load(stream)

		if maxLen != -1 and len(R) >= maxLen:
			hLen = len(R)
			newFirst = max(0, hLen-maxLen)
			R=R[newFirst:hLen]
		return R
		
	except:
		return {}

def yamlSave(data, fileName, safe_dump=True):
	f = open(fileName, 'w')

	if safe_dump:
		f.write(yaml.safe_dump(data, indent=4))
	else:
		f.write(yaml.dump(data, indent=4))

	f.close()




def load(fileName, LPC, addQuotes=False):
	# LPC : "lines per command"
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
	return CMDList