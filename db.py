#Working with mongo
import datetime

class DB:
	def __init__(self, dbdata):
		self.dbdata = dbdata

	def addTask(self, request):
		dir_tags = request.form["tags"]
		tags = dir_tags.split(',') if len(dir_tags) > 0 else None
		self.dbdata.insert({
			'task': request.form["tf"],\
			'marks':request.form["mark"],\
			'type':request.form["type_of_task"],\
			'description': request.form["descr"],\
			'date': datetime.datetime.utcnow(),\
			'complete': 0 if request.form["iscomplete"] == "no" else 1,\
			'tags': tags})

	def tasks(self):
		return list(self.dbdata.find())

	def current_tasks(self):
		return list(filter(lambda x: x['task'] if 'complete' not in x or \
			x['complete'] == 0 else None, self.tasks()))