from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
import sqlite3
from contextlib import closing
from flask_bootstrap import Bootstrap
from flask_wtf import Form, RecaptchaField
from wtforms import TextField, HiddenField, ValidationError,\
 SubmitField, IntegerField, FormField, TextAreaField, SelectField, validators
from wtforms.validators import Required, DataRequired, InputRequired

from pymongo import MongoClient

from learning import predict_success, gaussianPredict, getData, findOptimalTime
from util import *
from db import DB

import random
import os
import datetime

basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG=True
SECRET_KEY = 'secret'

app = Flask(__name__)
app.config.from_object(__name__)

mongo = MongoClient()
db = mongo.todo_db
tasks = db.tasks
trash = db.trash
dbdata = DB(tasks, trash)
class TodoForm(Form):
	tf = TextField("Task", [DataRequired("Enter your task")])
	descr = TextField("Desription")
	type_of_task = SelectField("Type of task", choices=(("study", "study"), \
		("read", "read"), \
		("fun", "fun"),
		("work", "work"),
		("programming", "programming")))
	priority_field = SelectField("Priority of task", choices = (("middle", "Middle"),\
		("low", "Low"), ("high", "High")))
	tags = TextField("Tags")

	#Replace for vetter solution
	deadline = IntegerField("Deadline")
	submit = SubmitField("Add")



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
	plan = TextField("planning", validators=[DataRequired()])

@app.route("/", methods=("GET", "POST"))
def main():
	form = TodoForm()
	sf = SearchForm()
	if request.method == 'POST':
		if len(form.tf.data) != 0:
			dbdata.addTask(request)
			alert = "alert alert-success"
			message = "Задача добавлена в список"
			targetFields = ["starttime", "time", "type"]
			result = gaussianPredict(targetFields, \
				[int(request.form["deadline"]) * 60,typeToNumber(request.form["type_of_task"]),\
				timeToNumber()], "complete")
			if result == 0:
				alert = "alert alert-success"
				rec_time = findOptimalTime(targetFields, \
					[int(request.form["deadline"]) * 60,typeToNumber(request.form["type_of_task"])],
					"complete")
				message = RECOMMEND_MESSAGE.format(numberToTime(rec_time))
			return render_template("index.html", form=form, sf=sf,
				thisdate=datetime.datetime.now(),tasks=dbdata.tasks_by_deadline_priority(),\
				message=message,\
				value=alert)
		else:
			dbdata.removeTasks(request.form)
			return render_template("index.html", form=form, \
				thisdate=datetime.datetime.now(),tasks=dbdata.tasks_by_deadline_priority(),\
				value="alert alert-success", message=\
				"Задачи удалены, но их можно восстановить")
	tags = dbdata.getTags()
	return render_template("index.html", form=form, sf=sf,
		thisdate=datetime.datetime.now(),tasks=dbdata.tasks_by_deadline_priority(),\
		tags = tags)

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

@app.route('/planning', methods=("GET", "POST"))
def planning():
	form = PlanningForm()
	if request.method == 'POST':
		if 'add' in request.form:
			names=[]
			for i in range(len(request.form)+1):
				name = 'plan{0}'.format(i)
				names.append(name)
				setattr(PlanningForm, name, TextField("Plan", [DataRequired("Enter your task")]))
			return render_template('planning.html', form=form, plans=names)
		if 'compute' in request.form:
			return 'TODO'
	else:
		form = PlanningForm()
		setattr(PlanningForm, 'plan0', TextField("Plan", [DataRequired("Enter your task")]))
		return render_template('planning.html', form=form, plans=['plan0'])

#TODO добавить отдельно базу для выполненных и текущих задач
#Предсказание оптимального времени выполнения задач
if __name__ == '__main__':
	Bootstrap(app)
	app.run()