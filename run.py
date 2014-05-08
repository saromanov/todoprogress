from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
import sqlite3
from contextlib import closing
from flask_bootstrap import Bootstrap
from flask_wtf import Form, RecaptchaField
from wtforms import TextField, HiddenField, ValidationError,\
 SubmitField, IntegerField, FormField, TextAreaField, SelectField, validators
from wtforms.validators import Required, DataRequired, InputRequired

from pymongo import MongoClient

from learning import predict_success
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
		("work", "work")))
	#mark = IntegerField("Your mark")
	#iscomplete = SelectField("This task is complete?", choices=(\
	#	("no", "No"),
	#	("yes", "Yes")))
	tags = TextField("Tags")
	submit = SubmitField("Add")


class SearchForm(Form):
	search = TextField("search", validators=[DataRequired()])

@app.route("/", methods=("GET", "POST"))
def main():
	form = TodoForm()
	sf = SearchForm()
	if request.method == 'POST':
		if len(form.tf.data) != 0:
			dbdata.addTask(request)
			return render_template("index.html", form=form, sf=sf,
				thisdate=datetime.datetime.now(),tasks=dbdata.tasks(),\
				message="Задача добавлена в список",\
				value="alert alert-success")
		else:
			#dbdata.removeTasks(request.form)
			return render_template("index.html", form=form, \
				thisdate=datetime.datetime.now(),tasks=dbdata.tasks(),\
				value="alert alert-success", message=\
				"Задачи удалены, но их можно восстановить")
	return render_template("index.html", form=form, sf=sf,
		thisdate=datetime.datetime.now(),tasks=dbdata.tasks())

@app.route("/list", methods=("GET", "POST"))
def show_list():
	dtasks = dbdata.tasks()
	size = len(dtasks)
	rem_size = len(dbdata.fromTrash())
	return render_template("list.html", tasks=zip(dtasks, list(range(size))),\
		trash=zip(dbdata.fromTrash(), list(range(rem_size))))



#TODO добавить отдельно базу для выполненных и текущих задач
#Предсказание оптимального времени выполнения задач
if __name__ == '__main__':
	Bootstrap(app)
	app.run()