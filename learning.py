from sklearn import linear_model
from sklearn.neighbors.nearest_centroid import NearestCentroid
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.feature_selection import SelectKBest
from sklearn.naive_bayes import MultinomialNB, GaussianNB, BernoulliNB
import numpy as np
import json
import os

def loadData(path):
	if not os.path.isfile(path):
		raise IOError("File not found")
	return json.loads(open(path).read())

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


#Split data on test set and train set

def Regression(X, y, pred_value):
	regr = linear_model.LogisticRegression()\
			.fit(X, y)\
			.predict(pred_value)


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

def gaussianPredict(cand):
	'''
	 	X, y = prepareData(data, ["starttime", "time", "type"], "complete")
	 	gaussianPredict(X, y, [2, 100, 2])
	 '''
	data = loadData("../task_data.json")
	data,target = prepareData(data, ["starttime", "time", "type"], "complete")
	funcs = [GaussianNB, MultinomialNB, BernoulliNB]
	minmissing = 99999999
	resultNB = None
	for nNB in funcs:
		bayes = nNB()
		fitting = bayes.fit(data, target)
		pred = fitting.predict(data)
		missing = (target != pred).sum()
		if missing < minmissing:
			minmissing = missing
			resultNB = fitting
	return resultNB.predict(cand)[0]

#TODO, make function for recommendation for better task on this time


#data = loadData("../task_data.json")
#X,y = prepareData(data, ["starttime", "time", "type"], "complete")
#print(gaussianPredict(X, y, [2, 100, 2]))




