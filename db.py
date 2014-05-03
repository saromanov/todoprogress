#Working with mongo

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
			'complete': request.form["iscomplete"],\
			'tags': tags})

	def tasks(self):
		return list(self.dbdata.find())