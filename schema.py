import datetime
from util import priorityToNumber, strToTime, timeToNumber, differenceToMinute

def getSchema1(request, tags):
	'''
		Schema for typical task
	'''
	return {
				'task': request.form["tf"],\
				'type':request.form["type_of_task"],\
				'description': request.form["descr"],\
				'date': datetime.datetime.utcnow(),\
				'mark':0,\
				'complete':0,\
				'priority':priorityToNumber(request.form["priority_field"]),\
				'deadline': datetime.datetime.now() + datetime.timedelta(hours = \
					int(request.form["deadline"])),\
				'tags': tags,
				'starttime': strToTime(request.form["starttime"])
			}

def getSchema2(request):
	'''
		Schema for attached task
	'''
	return {
				'task': request.form["tf"],\
				'type':request.form["type_of_task"],\
				'description': request.form["descr"],\
				'date': datetime.datetime.utcnow(),\
			}

def getSchema3(request, data):
	'''
		Schema for predict tasks
	'''
	return {
				'task': data['task'],\
				'type':data["type"],\
				'time': differenceToMinute(data['starttime']),\
				'mark': '0' if request['mark']=='' else request['mark'],
				'complete': data['complete'],
				'starttime': timeToNumber(data['starttime'])
			}