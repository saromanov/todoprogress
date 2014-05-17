#Working with mongo
import datetime
import pymongo
from bson.objectid import ObjectId
from util import priorityToNumber, completeToNumber

class DB:
	def __init__(self, dbdata, trash):
		'''
			dbdata - the main db for store information about tasks
			trash - tasks for remove, store after removeTasks
		'''
		self._dbdata = dbdata
		self._trash = trash

	def addTask(self, request):
		dir_tags = request.form["tags"]
		tags = dir_tags.split(',') if len(dir_tags) > 0 else None
		self._dbdata.insert({
			'task': request.form["tf"],\
			'type':request.form["type_of_task"],\
			'description': request.form["descr"],\
			'date': datetime.datetime.utcnow(),\
			'mark':0,\
			'iscomplete': '',\
			'priority':priorityToNumber(request.form["priority_field"]),\
			'deadline': datetime.datetime.now() + datetime.timedelta(hours = \
				int(request.form["deadline"])),\
			'tags': tags})

	def _appendData(self, taskid, field, value):
		'''
		 	append data for task
		'''
		self._dbdata.update({'_id': ObjectId(taskid)},{'$set': {field: value}}, upsert=False)
		print(list(self._dbdata.find()))

	def append(self, taskid, fields):
		for field in fields:
			if field != 'task_id':
				value = fields[field]
				if field == 'iscomplete':
					value = completeToNumber(value)
				self._appendData(taskid, field, completeToNumber(fields[field]))

	def tasks(self, sortby=None):
		if sortby == 'priority':
			return list(self._dbdata.find().sort([('priority', pymongo.DESCENDING)]))
		return list(self._dbdata.find())

	def current_tasks(self):
		return list(filter(lambda x: x['task'] if 'complete' not in x or \
			x['complete'] == 0 else None, self.tasks()))

	def find_by_name(self, name):
		return list(self._dbdata.find({'task': name}))

	def removeTasks(self, tasks, recover=True):
		'''
			tasks - list of task names
			recover - Remove tasks can be recovered from "trash"
		'''
		if len(tasks) != 0 and recover == True:
			for t in tasks:
				self._storeToTrash(self.find_by_name(t))
				self._dbdata.remove({'task': t})

	def _storeToTrash(self, tasksdata):
		self._trash.insert(tasksdata)

	def fromTrash(self):
		return list(self._trash.find())

	def loadTrainData(self, traindb):
		return list(traindb.find())