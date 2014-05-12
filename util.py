import datetime

#Some helpful functions

RECOMMEND_MESSAGE = "Вероятно, эта задача не будет выполнена в срок. \
Оптимальное время для начала задачи: "

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



