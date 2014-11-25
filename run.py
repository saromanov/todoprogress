from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
import sqlite3
from contextlib import closing
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from learning import predict_success, Predict, getData, findOptimalTime, \
planning_task_list, greedy_approach, find_similar_name
from util import *
from models import *
from db import DB

import random
import os
import datetime

#Formats

basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG=True
SECRET_KEY = 'secret'

app = Flask(__name__)
app.config.from_object(__name__)


try:
	mongo = MongoClient()
except Exception as e:
	raise PyMongoError("Error in mongo connecion. Check")

db = mongo.todo_db
tasks = db.tasks
trash = db.trash
dbdata = DB(db)
#For complete task prepare to append in training set
ct = []

#Check tasks after deadline
def pre_start():
	dbdata.storeBeforeDeadlineTasks()


@app.route("/", methods=("GET", "POST"))
def main():
	app.jinja_env.globals.update(currentTime=roundStartTimeNow)
	form = TodoForm()
	sf = SearchForm()
	if request.method == 'POST':
		if 'Add' in request.form:
			assert(isValidStartTime(request.form['starttime']) == 1)
			isadded = dbdata.addTask(request)
			if isinstance(isadded, Fail):
				return isadded.message
			alert = "alert alert-success"
			message = "Задача добавлена в список"
			targetFields = ["starttime", "time", "type"]
			result = Predict(targetFields, "complete", \
				[timeToNumber(isadded.obj), 5, typeToNumber(request.form["type_of_task"])],\
				dbdata.loadTrainData())

			print("THIS IS RESULT FOR PREDICT, ...", result)
			'''if result == 0 and timeToNumber(request.form['starttime']) != result:
				alert = "alert alert-success"
				rec_time = findOptimalTime(targetFields, \
					[int(request.form["deadline"]) * 60,typeToNumber(request.form["type_of_task"])],
					"complete")
				message = RECOMMEND_MESSAGE.format(numberToTime(rec_time))'''
			return render_template("index.html", form=form, sf=sf,
				thisdate=datetime.datetime.now(),tasks=dbdata.tasks_by_deadline_priority(),\
				message=message,\
				value=alert, attached=dbdata.getAttachedTasks())

		''' Добавить в цепь задач'''
		if 'AddChain' in request.form:
			dbdata.addTaskInChain(request)
			message = ''
			return render_template('index.html', form=form)

		if 'EndChain' in request.form:
			dbdata.endTaskFromChain(request.form)

		if 'Complete' in request.form:
			""" 
			Complete task append to store 
			a little "survey" after completion of task. Of course, need for prediction
			"""
			data = list(request.form.keys())
			if len(data) == 1:
				return redirect('/')
			data.remove('Complete')
			taskname = data[0]
			session['taskname'] = taskname
			return redirect(url_for('task'))

		#Начать работать над задачей
		if 'Work' in request.form:
			data = request.form
			for value in data:
				if value != 'Work':
					#Need to remove this part
					setwork = lambda x,value: dbdata.updateTask(value, 'isworking', x)
					if dbdata.isWorking(value):
						setwork(False,value)
					else:
						setwork(True,value)
			return render_template('index.html', form=form)

		#Закончить работать над задачей
		if 'StopWork' in request.form:
			for value in request.form:
				if value != 'Work':
					dbdata.updateTask(value, 'isworking', False)
			return render_template('index.html', form=form)
			
		elif 'Remove' in request.form:
			dbdata.removeTasks(request.form)
			message = getRemoveMessage(len(request.form))
			alert = "alert alert-info"
			return render_template("index.html", form=form, \
				thisdate=datetime.datetime.now(),tasks=dbdata.tasks_by_deadline_priority(),\
				message = message, value=alert)
	
	tags = dbdata.getTags()

	#dbdata.removeChainById()
	dbdata.getAttachedTasks()
	tasks = dbdata.tasks_by_deadline_priority()
	fromchain = dbdata.getFromChain()
	crontasks = dbdata.getTasksFromCron()
	return render_template("index.html", form=form, sf=sf,
		thisdate=datetime.datetime.now(),tasks=tasks,\
		tags = tags, taskcount=len(tasks),\
		attached=dbdata.getAttachedTasks(), chain=fromchain)

@app.route("/list", methods=("GET", "POST"))
def show_list():
	dtasks = dbdata.tasks()
	if request.method ==  'POST':
		task_id = request.form['task_id']
		dbdata.append(task_id, request.form)
		#dbdata.append
	return render_template("list.html", tasks=dtasks, attasks=dbdata.getAttachedTasks())


@app.route('/<tag>_tag', methods=("GET", "POST"))
def tag_info(tag=None):
	dtasks = dbdata.getByTag2(tag)
	return render_template('tag.html', tag=tag, tasks=dtasks)

@app.route('/task_<idd>', methods=("GET", "POST"))
def task_info(idd=None):
	if request.method == 'POST':
		req = request.form
		if 'Every_strt' in req and 'dayarea' in req and req['dayarea'].isdigit():
			dbdata.addTaskInCron(idd)
		if len(req['comment']) > 0:
			dbdata.appendData(idd, 'comments', request.form)
		return redirect('task_{0}'.format(idd))
	task = dbdata.find_by_id(idd)
	if task != None:
		info = TaskInfoForm()
		sim_tasks = find_similar_name(task['task'], dbdata=dbdata.pastTasks())
		if sim_tasks != None and len(sim_tasks) > 0:
			similar = list(map(lambda x: (x['task'], x['complete'], x['_id']), sim_tasks))
			print("THIS IS SIMILAR: ", similar)
			return render_template('task_info.html', task=task, forminfo=info, similar=similar)
	info = TaskInfoForm()
	return render_template('task_info.html', task=task, forminfo=info)

@app.route('/chain_<idd>', methods=("GET", "POST"))
def chain_info(idd=None):
	if request.method == 'POST':
		pass
	tasks = dbdata.getFromChain()
	return render_template('chain.html', tasks=tasks)


tasks = []
#Optimal planning for list of tasks
#TODO: Some breaks after complete of tasks
@app.route('/planning', methods=("GET", "POST"))
def planning():
	form = PlanningForm()
	if request.method == 'POST':
		if 'add' in request.form:
			if request.form['deadline'] == '':
				alert = "alert alert-warning"
				message = "Поле время на выполнение не заполнено"
				return render_template('planning.html', form=form, entasks=tasks, 
					value=alert, message=message)
			getform = request.form
			value = getform['deadline']
			if time_planning(getform['starttime'], getform['endtime']):
				return error_planning('Ошибка во времени задачи', form)
			try:
				result = int(value)
				tasks.append(request.form)
				return render_template('planning.html', form=form, entasks=tasks)
			except ValueError:
				return error_planning("Поле время на выполнение заполнено неверно", form)

		if 'compute' in request.form:
			if len(tasks) > 1:
				greedy_approach(tasks)
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

def time_planning(sttime, endtime):
	gett = lambda x: strToTime(x)
	return gett(sttime) == gett(endtime)

def error_planning(message, form):
	alert = "alert alert-warning"
	return render_template('planning.html', form=form, entasks=tasks, 
		value=alert, message=message)

@app.route('/task', methods=("GET", "POST"))
def task():
	if request.method == 'POST':
		if 'append' in request.form:
			#Append in training set
			if len(ct) > 0:
				comptask = ct.pop()
				comptask['complete'] = '1'
				dbdata.appendinTS(request.form, comptask)
				dbdata.removeTasks([comptask['task']])
			return redirect('/')
	bff = BeforeTaskForm()
	current = dbdata.find_by_name(session['taskname'])
	if current != None and len(current) > 0:
		ct.append(current)
	return render_template('task.html', form=bff, taskname=session['taskname'])

@app.route('/login', methods=("GET", "POST"))
def login():
	login = Login()
	return render_template('login.html', form=login)

#TODO добавить отдельно базу для выполненных и текущих задач
#Предсказание оптимального времени выполнения задач
if __name__ == '__main__':
	Bootstrap(app)
	pre_start()
	app.run()


#Добавить стэк задач (новая задача, активируется, когда завершается текущая)

#Подсказка, сколько может занять задача



