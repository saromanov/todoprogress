from sklearn import linear_model
from sklearn.neighbors.nearest_centroid import NearestCentroid
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.feature_selection import SelectKBest
from sklearn.naive_bayes import MultinomialNB, GaussianNB, BernoulliNB
from sklearn.linear_model import Ridge, Lasso, LinearRegression
from sklearn.cluster import KMeans
import numpy as np
import json
import os
from math import log, sqrt
from util import numberToTime, strToTime, timeToNumber, tasknameToPretty
from datetime import timedelta
import itertools

import db

def loadData(path):
	'''
		Load data from file. Probably only for test
	'''
	if not os.path.isfile(path):
		raise IOError("File not found")
	return json.loads(open(path).read())

def loadDataFromMongo(dbdata):
	'''
		Load data from Mongodb if is exist
	'''
	tasks = dbdata.tasks()

def prepareData(datajson, fields, param=None):
	'''
	datastore - data in json format
	fields - fields will be use in learning
	param - target value for predict
	'''

	X = []
	y = []
	for v in datajson:
		data = datajson[v]
		temp = []
		for f in fields:
			temp.append(data[f])
		X.append(temp)
		if param != None:
			y.append(data[param])
	return X,y


def getTargetFields(data, fields):
	""" Return only data from target fields 
		data in format key-value
	"""
	return [list(map(lambda x:data[train][x], \
		filter(lambda x: x in fields, data[train]))) \
		for train in data]


def getData(request, fields):
	'''
		Clean and get data from task form
	'''
	return list(filter(lambda x: request[x] != None, fields))

#Split data on test set and train set

def Regression(X, y, pred_value, model):
	regr = model()\
			.fit(X, y)\
			.predict(pred_value)
	return regr


#Clustering current task on hard, medium and easy
def task_clustering(X, y, pred_value):
	return NearestCentroid()\
		   .fit(X, y)\
		   .predict(pred_value)


#Predict on succes or failure of task
def predict_success(X, y, pred_value, threshold):
	True if Regression(X, y, pred_value) >= threshold else False




#Find similar tasks
def find_similar_tasks(X, y):
	'''
		Get list of most probable tasks from task name and tags
		names=['name_1', name_n']

		X,y = prepareData(loadData("../task_data.json"), ['task'], 'complete')
	'''
	clear = [i[0] for i in X]
	vect = CountVectorizer()
	vmatrix = vect.fit_transform(clear)

	tfifd = TfidfVectorizer(stop_words="english")
	X_train = tfifd.fit_transform(clear)
	ch = SelectKBest()
	result = ch.fit_transform(X_train, y)
	return ch.fit_transform(X_train, y)


#Load data for compare task names
def loadTasks(data):
	result = None
	if 'data' in data:
		result = loadData(path).keys()
	if 'dbdata' in data:
		return data['dbdata']	
	if result == None:
		return 

def hamming_distance_loop(current, base):
	"""
		current - target taskname
		base - optimal task
		all in the list format
	"""

	#Prepare operation - remove all words with length 1 or 2
	#Probably need to remove
	prepared = lambda word: filter(lambda x: len(x) > 2, word)
	result = .0
	value1 = list(prepared(current))
	value2 = list(prepared(base))
	for word1,word2 in zip(value1, value2):
		result += hamming_distance_extended(word1, word2)
	return result

def hamming_distance_extended(current, baseword):
	""" 
		Extended version of Hamming distance, where every mismatch have a cost.
		Mistmatching on the start or at the end of the word
		have a lss cost, then mismatching in the center of the word
		TODO: Добавить вариант со смещением слова
	"""
	longer_word = max(current, baseword)
	short_word = min(current, baseword)
	longer_length = len(longer_word)
	distr = list(map(lambda x: x/longer_length if x <= longer_length/2 else 1 - (x/longer_length),\
		range(1,longer_length+1)))
	distr[-1] = distr[0]
	score = .0
	for pos, word in enumerate(longer_word):
		if pos >= len(short_word):
			return abs(score)/len(longer_word)
		if word != short_word[pos]:
			score += abs(distr[pos])
	return abs(score)/len(longer_word)

def find_similar_name(target, *args, **kwargs):
	'''
		Get most similar names on current task from db
		Simple compute count of identical words
	'''
	data = loadTasks(kwargs)
	if data == None: return []
	results = []
	maxdiff = 0
	splitter = tasknameToPretty(target)
	print(target)
	for w in data:
		value = w['task'].lower().split()
		#Добавить к общему сравнению
		hamming = hamming_distance_loop(splitter, value)
		result = value + splitter
		old = len(result)
		diff = old - len(set(result))
		if diff > maxdiff:
			maxdiff = diff
			results = []
			results.append(w)
			continue
		if maxdiff != 0 and diff == maxdiff:
			results.append(w)
	return results


def find_similar_name_log(data, target):
	results = []
	splitter = target.lower().split()
	maxdift = 0
	task = None
	for w in data:
		value = data[w]['task'].lower().split()
		result = 0.0
		for t in splitter:
			result += compute_distance(value, splitter, t)
		if result != 0 and log(result) > maxdift:
			maxdiff = log(result)
			task = data[w]
			results.append(task)
	return task, results

def compute_distance(original, target, word):
	if word in original and word in target:
		original_pos = original.index(word)+1
		target_pos = target.index(word)+1
		diff = sqrt(abs(original_pos**2 - target_pos**2))
		res_diff = 1 if diff == 0 else diff
		return len(original)/(res_diff * len(target)) * \
			original_pos/ target_pos + (original_pos/len(original))
	else:
		return 0


def gaussianPredict(fields, target_data, cand):
	'''
		Predict for complete of current task
	 	X, y = prepareData(data, ["starttime", "time", "type"], "complete")
	 	gaussianPredict(X, y, [2, 100, 2])
	 '''
	funcs = [GaussianNB, MultinomialNB, BernoulliNB]
	minmissing = 99999999
	resultNB = None
	predvalue = None
	for nNB in funcs:
		bayes = nNB()
		fitting = bayes.fit(fields, target_data)
		pred = fitting.predict(cand)
		missing = (target_data != pred).sum()
		if missing < minmissing:
			minmissing = missing
			resultNB = fitting
			predvalue = pred
	return predvalue


def Predict(fields, targ_field, cand, traindata):
	'''
		TODO: Return list of similar tasks
	'''
	#Just for test
	#Analysis for tags and for task title
	data = loadData("../task_data.json")
	#Fix to 10
	if len(traindata) > 2:
		string_data = getTargetFields(data,['task', 'tags'])
		print(string_data, ...)
		X, y = prepareData(data, fields, targ_field)
		return gaussianPredict(X, y, cand)

#Find optimal time for success this task
def findOptimalTime(fields, target, cand):
	values = [0,1,2,3]
	for f in values:
		result = gaussianPredict(fields, [f] + target, cand)
		if result == 1:
			return f


def estimateTrainingData(data, fields, values, avalues, cand):
	'''
		data - training data loaded from db
		Estimate amount on training data
	'''
	data,target = prepareData(data, fields, cand)
	start_predict = gaussianPredict(fields, values, cand)
	for i in range(10):
		data.append(avalues)


def simple_distance(actual, targets):
	mindist = 99999
	result = None
	for t in targets:
		value = 0
		for param in actual:
			value += abs(param - t)
		if value < mindist:
			mindist = value
			result = t
	return result

def planning_tasks(data, tasklist):
	'''
		data - data for learning
		tasklist - current tasks
	'''
	predicts = []
	regrs = [LinearRegression, Ridge, Lasso]
	for d in tasklist:
		optimal_task, tasks = find_similar_name_log(data, d['task'])
		currenttask = d['task']
		del d['task']
		X,y = prepareData(data, d.keys(), 'starttime')
		values = []
		if len(tasks) > 1:
			for r in regrs:
				values.append(Regression(X, y, [d['time'], d['type']], r))
			predicts.append((currenttask, simple_distance(values, [0,1,2,3])))
		else:
			predicts.append((currenttask,-1))
	return predicts


def show_planning_tasks(data):
	result = []
	for d in data:
		taskname, optime = d
		result.append((taskname, numberToTime(optime)))
	return result

def prepare_to_greedy(data):
	result = []
	for d in data:
		result.append((strToTime(d['starttime']), 
			strToTime(d['endtime']), int(d['deadline'])))
	return result

def prepare_to_greedy2(data):
	return [[res[2] * 60, timeToNumber(res[0]), res[3], res[4]] for res in data],\
		   [[res[0], res[1], res[2] * 60, res[3], res[4]] for res in data]

def greedy_approach(data, traindata):
	'''
	Plannin optimal task list without ml algorithms,
	but only with "naive" greedy approach
	'''
	#resdata = prepare_to_greedy(data)
	resdata = data
	result = []
	last = 0
	result.append(1)

	#List with "waiting events"
	waitlist = []
	resdata = sorted(data, key=lambda x: x[0] - x[1], reverse=True)
	for current in range(2,len(data)):
		first = resdata[current]
		opt = isOptimal(first, traindata)
		if first[0] <= resdata[last][0] and opt:
			result.append(current)
			last = current
	return list(map(lambda x: resdata[x][4], result))


def isOptimal(task, train):
	'''
	TODO
	Нахолждение оптимального времени для задачи
	'''
	return True

def getOptimalTime(task):
	store = loadData('../task_data.json')
	data = prepareData(store, ['time', 'starttime', 'type'], 'complete')
	print(greedy_approach(task, data))



def planning_task_list(data):
	'''
		list of tasks to optimal time for working on them
	'''
	tasklist = make_clear_data(data)
	store = loadData('../task_data.json')
	plan = planning_tasks(store, tasklist)
	greedy = greedy_approach(data)
	return show_planning_tasks(plan)


def make_clear_data(data):
	return [{'type': d['ttype'], 'task': d['tf'], 'time': int(d['deadline'])*60}
		for d in data]


def clustering_tasks(X,y, cand):
	if X == None or y == None:
		raise Exception("Data is undefined")
	kmeans = KMeans(init="k-means++", n_clusters=3, n_init=10).fit(X,y)
	kmeans.predict(cand)


def test_greedy():
	import datetime
	t1 = datetime.timedelta(hours=24)
	t2 = datetime.timedelta(hours=12)
	t3 = datetime.timedelta(hours=48)
	now = datetime.datetime.now()
	data = [[now, (now + t1), 5,0, "A"], [now, (now + t1),2,2,"B"], \
	[now, (now + t2),1,2,"C"], \
	[now, (now + t3), 4,0,"D"], [now, (now + t1),3,0,"E"]]
	prep, tolearn = prepare_to_greedy2(data)
	getOptimalTime(tolearn)
	#greedy_approach(data)
