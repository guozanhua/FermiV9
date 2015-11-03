import parsedatetime


def fixStr(inStr):
	inStr = inStr.lower()

	if "from now" not in inStr and "in " in inStr:
		inStr = inStr.replace("in ", " ")
		inStr = inStr+" from now"

	inStr = inStr.replace("by ", " ")
	inStr = inStr.replace("a little while", "10 minutes")
	inStr = inStr.replace("a while", "30 minutes")
	inStr = inStr.replace("a couple", "2")
	inStr = inStr.replace("a few", "3")
	inStr = inStr.replace("some time", "2 hours")
	inStr = inStr.replace("several", "6")
	inStr = inStr.replace("midnight", "11:59 pm")
	inStr = inStr.replace("soon", "30 minutes from now")

	inStr = inStr.replace("half hour", "30 minutes")
	inStr = inStr.replace("half an hour", "30 minutes")
	inStr = inStr.replace("half a day", "12 hours")

	return inStr

def getTimeVec(inStr):
	cal = parsedatetime.Calendar()
	[T, worked] = cal.parse(fixStr(inStr))

	T  = [item for item in T]

	#if worked == 0:
	#	print "PARSE FAILED"

	#time.struct_time(tm_year=2015, tm_mon=7, tm_mday=3, tm_hour=4, tm_min=6, tm_sec=36, tm_wday=4, tm_yday=184, tm_isdst=-1)

	Year = T[0]
	Month = T[1]
	DayOfMonth = T[2]
	Hour24 = T[3]
	Minute = T[4]
	Second = T[5]
	Weekday = T[6]
	DayOfYear = T[7]

	#NOW = cal.parse("now")

	return {"year":Year, "month":Month, "day":DayOfMonth, "hour":Hour24, "minute":Minute, "second":Second, "worked":worked!=0}

