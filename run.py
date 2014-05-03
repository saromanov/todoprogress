from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
import sqlite3
from contextlib import closing
from flask_bootstrap import Bootstrap
from flask_wtf import Form, RecaptchaField
from wtforms import TextField, HiddenField, ValidationError,\
 SubmitField, IntegerField, FormField, TextAreaField, SelectField, validators
from wtforms.validators import Required, DataRequired

from pymongo import MongoClient

from learning import predict_success

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
#app.session_interface = MongoEngineSessionInterface(db)
class TodoForm(Form):
	tf = TextField("Task", validators=[DataRequired()])
	descr = TextField("Desription", validators=[DataRequired()])
	type_of_task = SelectField("Type of task", choices=(("study", "study"), \
		("read", "read"), \
		("fun", "fun"),
		("work", "work")))
	mark = IntegerField("Your mark", validators=[DataRequired()])
	iscomplete = SelectField("This task is complete?", choices=(("yes", "Yes"),\
		("no", "No")))
	tags = TextField("Tags")
	submit = SubmitField("Add")


class SearchForm(Form):
	search = TextField("search", validators=[DataRequired()])

@app.route("/", methods=("GET", "POST"))
def main():
	form = TodoForm()
	sf = SearchForm()
	if request.method == 'POST':
		dir_tags = request.form["tags"]
		tags = dir_tags.split(',') if len(dir_tags) > 0 else None
		tasks.insert({
			'task': request.form["tf"],\
			'marks':request.form["mark"],\
			'type':request.form["type_of_task"],\
			'description': request.form["descr"],\
			'date': datetime.datetime.utcnow(),\
			'complete': request.form["iscomplete"],\
			'tags': tags})

		'''return render_template("index.html", form=form, sf=sf, pred = pr,\
		thisdate=datetime.datetime.now(),\
		tasks=list(tasks.find()), score=predict_success(X, y, pred_value, threshold)'''
		redirect('done')
	return render_template("index.html", form=form, sf=sf,\
		thisdate=datetime.datetime.now(),\
		tasks=list(tasks.find()))

@app.route("/list", methods=("GET", "POST"))
def show_list():
	dtasks = list(tasks.find())
	size = len(dtasks)
	return render_template("list.html", tasks=zip(dtasks, list(range(size))))



#TODO добавить отдельно базу для выполненных и текущих задач
#Предсказание оптимального времени выполнения задач
if __name__ == '__main__':
	Bootstrap(app)
	app.run()