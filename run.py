from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
import sqlite3
from contextlib import closing
from flask_bootstrap import Bootstrap
from flask_wtf import Form, RecaptchaField
from wtforms import TextField, HiddenField, ValidationError, RadioField,\
    BooleanField, SubmitField, IntegerField, FormField, validators
from wtforms.validators import Required, DataRequired


from pymongo import MongoClient

#from gevent import pywsgi, socket
#from geventwebsocket.handler import WebSocketHandler
#from flask.ext.sqlalchemy import SQLAlchemy
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
	your_mark = IntegerField("Your mark for this task", validators=[DataRequired()])
	#List
	type_task = TextField("Type of your task", validators=[DataRequired()])
	submit = SubmitField("Send")

@app.route("/", methods=("GET", "POST"))
def main():
	form = TodoForm()
	if request.method == 'POST':
		tasks.insert({'task': request.form["tf"],\
			'mark':request.form["your_mark"],\
			'type':request.form["type_task"],\
			'description': request.form["descr"],\
			"date": datetime.datetime.utcnow()})
		redirect('done')
	return render_template("index.html", form=form, thisdate=datetime.datetime.now())

@app.route("/list", methods=("GET", "POST"))
def show_list():
	return render_template("list.html", tasks=list(tasks.find()))


if __name__ == '__main__':
	Bootstrap(app)
	app.run()