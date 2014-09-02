#Working with mongo
import datetime
import pymongo
from bson.objectid import ObjectId
from schema import getSchema1, getSchema2, getSchema3, getSchema4
from util import priorityToNumber, completeToNumber, checkDeadline, strToTime,\
isAfterDeadline, Fail, Success, deadlineToTime




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
		self._chains = dbdata.chains

	def _getTags(self, tags):
		return tags.replace(' ','').split(',') if len(tags) > 0 else None

	def _checkTypeDeadline(self, request):
		'''
			Check if type of deadline is structed or in hour
		'''
		if request['deadline'] == '':
			return Success(deadlineToTime(request['deadlinefield']))
		else:
			return Success(datetime.datetime.now() + datetime.timedelta(hours = \
				int(request["deadline"])))

	def addTask(self, request):
		tags = self._getTags(request.form["tags"])
		deadline = self._checkTypeDeadline(request.form)
		if isinstance(deadline, Fail):
			return Fail(deadline.message)
		dedalineobj = deadline.obj
		if request.form['attached'] == 'no':
			self._dbdata.insert(getSchema1(request, tags, dedalineobj))
			return deadline
		else:
			self._attached.insert(getSchema2(request))
			return deadline

	def addTaskInChain(self, request):
		'''
			In future, can be several chains
		'''
		deadline = self._checkTypeDeadline(request.form)
		if isinstance(deadline, Fail):
			return Fail(deadline.message)
		dedalineobj = deadline.obj
		tags = self._getTags(request.form["tags"])
		if self.isEmptyTaskChain():
			self._chains.insert({'name': 'default', 'tasks': [getSchema1(request, tags, dedalineobj)]})
		else:	
			self._chains.update({'name': 'default'}, {'$push': {'tasks': getSchema1(request, tags, dedalineobj)}})

	def isEmptyTaskChain(self, id='default'):
		tasks = self.getFromChain()
		return True if tasks == None else False

	def removeChainById(self, idd='default'):
		self._chains.remove({'name': idd})

	def getFromChain(self):
		tasks = self._chains.find_one()
		if tasks != None and 'tasks' in tasks:
			return tasks['tasks']

	def endTaskFromChain(self, request):
		for rec in request:
			if rec != 'EndChain':
				self._chains.update({'name': 'default'}, {'$pull': {'tasks': {'task': rec}}})
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

	def isWorking(self, taskname):
		return self._dbdata.find_one({'task': taskname})['isworking'] == True

	def appendData(self, taskid, field, request):
		self._appendData(taskid, field, getSchema4(request), '$addToSet')

	def updateTask(self, tasktitle, field, param):
		self._dbdata.update({'task': tasktitle}, {'$set': {field: param}}, upsert=False)

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

	def removeAll(self):
		self._dbdata.remove()

	def _storeToTrash(self, tasksdata):
		result = self._dbdata.find_one({'task': tasksdata})
		if result != None:
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

