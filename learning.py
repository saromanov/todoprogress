from sklearn import linear_model
from sklearn.neighbors.nearest_centroid import NearestCentroid
import numpy as np
import json

#Load data from json
def loadData(path, fields, params):
	X = []
	y = []
	value = json.loads(open(path).read())
	for v in value:
		data = value[v]
		temp = []
		for f in fields:
			temp.append(data[f])
		X.append(temp)
		y.append(data[params])
	return X,y

def Regression(X, y, pred_value):
	regr = linear_model.BayesianRidge()\
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


