#Working with mongo
import datetime
import pymongo
from bson.objectid import ObjectId
from schema import getSchema1, getSchema2, getSchema3, getSchema4
from util import priorityToNumber, completeToNumber, checkDeadline, strToTime,\
isAfterDeadline

class DB:
	def __init__(self, dbdata):
		'''
			dbdata - the main db for store information about tasks
			trash - tasks for remove, store after removeTasks
		'''
		self._dbdata = dbdata.tasks
		self._trash = dbdata.tasks
		self._attached = dbdata.attached
		self._training = dbdata.training

	def addTask(self, request):
		dir_tags = request.form["tags"]
		tags = dir_tags.replace(' ','').split(',') if len(dir_tags) > 0 else None
		if request.form['attached'] == 'no':
			self._dbdata.insert(getSchema1(request, tags))
		else:
			#Почитать про добавление в различные базы для
			#Группы закреплённые
			self._attached.insert(getSchema2(request))

	def _appendAttachedTask(self, schema):
		self._attached.insert(schema)

	def getAttachedTasks(self):
		return list(self._attached.find())

	def _appendData(self, taskid, field,schema, action='$add'):
		'''
		 	append data for task
		'''
		self._dbdata.update({'id': taskid},{action: {field: schema}}, upsert=False)



	def append(self, taskid, fields):
		for field in fields:
			if field != 'task_id':
				value = fields[field]
				if field == 'iscomplete':
					value = completeToNumber(value)
				self._appendData(taskid, field, completeToNumber(fields[field]))

	def appendData(self, taskid, field, request):
		self._appendData(taskid, field, getSchema4(request), '$addToSet')

	def tasks(self, *args, **kwargs):
		return list(self._dbdata.find())

	def tasks_by_deadline_priority(self):
		ctasks = self.tasks()
		before = list(filter(lambda x: isAfterDeadline(x['deadline']), ctasks))
		request = {'mark':'0'}
		for data in before:
			data['complete'] = '0'
			self.appendinTS(request, data)
		return list(self._dbdata.find({'deadline': {'$gt': datetime.datetime.now()}})\
		                .sort('priority', pymongo.DESCENDING))

	def _tasks_before_deadline(self, tasksdata):
		return tasksdata.find({'deadline': {'$gt': datetime.datetime.now()}}).sort('priority', pymongo.DESCENDING)

	def current_tasks(self):
		return list(filter(lambda x: x['task'] if 'complete' not in x or \
			x['complete'] == 0 else None, self.tasks()))

	def find_by_name(self, name):
		return self._find('name', name)

	def find_by_id(self, idvalue):
		return self._dbdata.find_one({'id': idvalue})

	def _find(self, field, data):
		return list(self._dbdata.find({field: data}).sort(field))

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
		result = self._dbdata.find_one({'task': tasksdata})
		if result != None:
			print("THIS task was append: ")
			self._trash.insert(result)
		#self._trash.insert({'taskname': tasksdata})

	def fromTrash(self):
		return list(self._trash.find())

	def loadTrainData(self, traindb):
		return list(traindb.find())

	#Get tasks by tag
	def getByTag(self, tag):
		return list(self._dbdata.find({'tags': {"$all": [tag]}}))

	#Get tasks by tag
	def getByTag2(self, tag):
		return list(self._dbdata.find({'tags': {"$in":[tag]}}))

	def getTags(self):
		taskdata = self.tasks()
		tags = []
		for td in taskdata:
			if 'tags' in td and td['tags'] != None:
				for t in td['tags']:
					tags.append(t)
		return set(tags)


	#Append in training set for predict optimal tasks
	def appendinTS(self, request, data):
		schema = getSchema3(request, data)
		self._training.insert(schema)

