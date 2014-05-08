#Working with mongo
import datetime

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
			'deadline': datetime.datetime.now() + datetime.timedelta(hours = \
				int(request.form["deadline"])),\
			'tags': tags})

	def appendData(self, taskname, field, value):
		'''
		 	append data for task
		'''
		task = self._dbdata.find({name: taskname})
		if len(task) > 0:
			self._dbdata.update({name: taskname, field: value})

	def tasks(self):
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

