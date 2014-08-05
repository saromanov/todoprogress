import datetime
from time import mktime, time, strptime
import builtins
from uuid import uuid4

#Some helpful functions

RECOMMEND_MESSAGE = "Оптимальное время для начала задачи: {0}"
RECOVER_MESSAGE = "Задачи удалены, но их можно восстановить"

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

def timeToNumber(currtime=None):
	'''
		input: currtime in str format
		output:
		0 - morning
		1 - afternoon
		2 - evening
		3 - night

		example: 2014-07-23 20:42:43 => 2
	'''
	if currtime == None:
		now = datetime.datetime.now().hour
	if type(currtime) == builtins.str:
		now = strToTime(currtime).hour
	else:
		now = currtime.hour
	if now >= 0 and now <= 5:
		return 3
	if now >= 6 and now <= 11:
		return 0
	if now >= 12 and now <= 5:
		return 1
	else:
		return 2

def numberToTime(value):
	if value == 0:
		return "Утро"
	if value == 1:
		return "День"
	if value == 2:
		return "Вечер"
	if value == 3:
		return "Ночь"


def typeToNumber(value):
	if value == "study":
		return 0
	if value == "read":
		return 1
	if value == "fun":
		return 2
	if value == "work":
		return 3
	if value == "programming":
		return 4

def checkDeadline(data):
	'''
		Check how much time is left to deadline
		data - "2014-05-09 07:37:50"
	'''
	return strToTime(data) - datetime.datetime.now()

def isAfterDeadline(data):
	'''
	data - 2014-05-09 07:37:50
	output: 1 is time for this task after deadline, 
	1 in otherwise
	'''
	return data < datetime.datetime.now()

def isValidStartTime(data):
	result = 0
	try:
		result = 0 if checkDeadline(data) < datetime.timedelta() else 1
		return result
	except Exception as e:
		return result

def strToTime(timedata):
	try:
		return datetime.datetime.fromtimestamp(mktime(strptime(timedata, TIME_FORMAT)))
	except Exception:
		raise 'Error in the time format'

def defaultTime(d=datetime.datetime.now()):
	return d.strptime(d.strftime(TIME_FORMAT), TIME_FORMAT)


def priorityToNumber(priority):
	if priority == 'low':
		return 0
	if priority == 'middle':
		return 1
	if priority == 'high':
		return 2


def completeToNumber(iscomplete):
	if iscomplete == 'no':
		return 0
	if iscomplete == 'yes':
		return 1


def roundStartTime(data):
	if type(data) == builtins.str:
		data = strToTime(data)
	value = lambda minu: data + datetime.timedelta(minutes=minu)
	result = data.minute
	if result % 5 == 0:
		return value(5)
	c = 0
	for x in range(1,5):
		c += 1
		if (result+c) % 5 == 0:
			return value(c)

def roundStartTimeNow():
	d = datetime.datetime.now()
	return roundStartTime(datetime.datetime.now().strptime(d.strftime(TIME_FORMAT), TIME_FORMAT))

def differenceToMinute(data):
	res = datetime.datetime.now() - data
	return divmod(res.days * 86400 + res.seconds, 60)[0]


def genTaskId():
	return str(uuid4())


