import datetime
from time import mktime, time

#Some helpful functions

RECOMMEND_MESSAGE = "Вероятно, эта задача не будет выполнена в срок. \
Оптимальное время для начала задачи: {0}"

def timeToNumber():
	'''
		0 - morning
		1 - afternoon
		2 - evening
		3 - night
	'''
	now = datetime.datetime.now().hour
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
	value = time.strptime(data, "%Y-%m-%d %H:%M:%S")
	dt = datetime.datetime.fromtimestamp(mktime(value))
	return dt - datetime.datetime.now()


def priorityToNumber(priority):
	if priority == 'low':
		return 0
	if priority == 'middle':
		return 1
	if priority == 'high':
		return 2



