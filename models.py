from wtforms import TextField, HiddenField, ValidationError,\
 SubmitField, IntegerField, FormField, TextAreaField, SelectField, validators, DateTimeField,\
 PasswordField
from wtforms.validators import Required, DataRequired, InputRequired
from peewee import Model
from flask_bootstrap import Bootstrap
from flask_wtf import Form, RecaptchaField

from util import *

TypeOfTaskField = SelectField("Type of task", choices=(("study", "study"), \
		("read", "read"), \
		("fun", "fun"),
		("work", "work"),
		("programming", "programming")))

#Move ths stuff to models file
class TodoForm(Form):
	tf = TextField("Task")
	descr = TextField("Desription")
	type_of_task = TypeOfTaskField
	priority_field = SelectField("Priority of task", choices = (("middle", "Middle"),\
		("low", "Low"), ("high", "High")))
	tags = TextField("Tags")
	starttime = DateTimeField(default= roundStartTime(datetime.datetime.now()))

	#Replace for vetter solution
	deadline = IntegerField("Deadline")
	submit = SubmitField("Add")



class BaseModel(Model):
	join_field = DateTimeField()
class BeforeTaskForm(Form):
	'''
		Adding information after completion of task
	'''

	#Replace for better solution
	task_id = TextField("task", [validators.required()])
	mark = IntegerField("Your mark", [validators.required(), validators.length(max=10)])
	iscomplete = SelectField("This task was complete before deadline?", choices=(\
		("no", "No"),
		("yes", "Yes")))



class SearchForm(Form):pass


class PlanningForm(Form):
	tf = TextField("Task")
	ttype = TypeOfTaskField
	deadline = TextField("deadline", description="A")
	starttime = DateTimeField(default=defaultTime)
	endtime = DateTimeField(default=defaultTime)



class Login(Form):
	nick = TextField("nickname")
	password = PasswordField("password")