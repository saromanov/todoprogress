from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
import sqlite3
from contextlib import closing
from flask_bootstrap import Bootstrap
from flask_wtf import Form, RecaptchaField
from wtforms import TextField, HiddenField, ValidationError,\
 SubmitField, IntegerField, FormField, TextAreaField, SelectField, validators, DateTimeField,\
 PasswordField
from wtforms.validators import Required, DataRequired, InputRequired
from peewee import Model

from pymongo import MongoClient

from learning import predict_success, gaussianPredict, getData, findOptimalTime, \
planning_task_list
from util import *
from db import DB

import random
import os
import datetime

basedir = os.path.abspath(os.path.dirname(__file__))

TypeOfTaskField = SelectField("Type of task", choices=(("study", "study"), \
		("read", "read"), \
		("fun", "fun"),
		("work", "work"),
		("programming", "programming")))

DEBUG=True
SECRET_KEY = 'secret'

app = Flask(__name__)
app.config.from_object(__name__)

mongo = MongoClient()
db = mongo.todo_db
tasks = db.tasks
trash = db.trash
dbdata = DB(tasks, trash)


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
	task_id = TextField("task")
	mark = IntegerField("Your mark")
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

@app.route("/", methods=("GET", "POST"))
def main():
	form = TodoForm()
	sf = SearchForm()
	if request.method == 'POST':
		if len(form.tf.data) != 0:
			assert(isValidStartTime(request.form['starttime']) == 1)
			dbdata.addTask(request)
			alert = "alert alert-success"
			message = "Задача добавлена в список"
			targetFields = ["starttime", "time", "type"]
			result = gaussianPredict(targetFields, \
				[int(request.form["deadline"]) * 60,typeToNumber(request.form["type_of_task"]),\
				timeToNumber()], "complete")
			if result == 0 and timeToNumber(request.form['starttime']) != result:
				alert = "alert alert-success"
				rec_time = findOptimalTime(targetFields, \
					[int(request.form["deadline"]) * 60,typeToNumber(request.form["type_of_task"])],
					"complete")
				message = RECOMMEND_MESSAGE.format(numberToTime(rec_time))
			return render_template("index.html", form=form, sf=sf,
				thisdate=datetime.datetime.now(),tasks=dbdata.tasks_by_deadline_priority(),\
				message=message,\
				value=alert)

		#a little "survey" after completion of task. Of course, need for prediction
		if 'Complete' in request.form:
			data = list(request.form.keys())
			if len(data) == 1:
				return redirect('/')
			taskname = data[0]
			bff = BeforeTaskForm()
			return render_template("list.html", form=bff, taskname=taskname)
		elif 'Remove' in request.form:
			dbdata.removeTasks(request.form)
			return render_template("index.html", form=form, \
				thisdate=datetime.datetime.now(),tasks=dbdata.tasks_by_deadline_priority(),\
				value="alert alert-success", message=RECOMMEND_MESSAGE)
	tags = dbdata.getTags()
	return render_template("index.html", form=form, sf=sf,
		thisdate=datetime.datetime.now(),tasks=dbdata.tasks_by_deadline_priority(),\
		tags = tags, taskcount=len(dbdata.tasks_by_deadline_priority()))

@app.route("/list", methods=("GET", "POST"))
def show_list():
	dtasks = dbdata.tasks()
	size = len(dtasks)
	rem_size = len(dbdata.fromTrash())
	bftform = BeforeTaskForm()
	if request.method ==  'POST':
		task_id = request.form['task_id']
		dbdata.append(task_id, request.form)
		#dbdata.append
	return render_template("list.html", bftform = bftform, tasks=zip(dtasks, list(range(size))),\
		trash=zip(dbdata.fromTrash(), list(range(rem_size))))


@app.route('/<tag>_tag', methods=("GET", "POST"))
def tag_info(tag=None):
	dtasks = dbdata.getByTag2(tag)
	return render_template('tag.html', tag=tag, tasks=dtasks)

tasks = []
@app.route('/planning', methods=("GET", "POST"))
def planning():
	form = PlanningForm()
	if request.method == 'POST':
		if 'add' in request.form:
			tasks.append(request.form)
			return render_template('planning.html', form=form, entasks=tasks)
		if 'compute' in request.form:
			if len(tasks) > 1:
				return render_template('planning.html', form=form, 
					plantasks=planning_task_list(tasks))
			else:
				return redirect('planning')
		if 'clearall' in request.form:
			tasks.clear()
			return render_template('planning.html', form=form)
	else:
		form = PlanningForm()
		return render_template('planning.html', form=form)


@app.route('/task', methods=("GET", "POST"))
def task():
	if request.method == 'POST':
		if 'append' in request.form:
			return "A"
			#dbdata.append(123, request.form)
	bff = BeforeTaskForm()
	return render_template('task.html', form=bff)

@app.route('/login', methods=("GET", "POST"))
def login():
	login = Login()
	return render_template('login', form=login)

#TODO добавить отдельно базу для выполненных и текущих задач
#Предсказание оптимального времени выполнения задач
if __name__ == '__main__':
	Bootstrap(app)
	app.run()

