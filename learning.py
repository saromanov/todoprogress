from sklearn import linear_model, SGDClassifer
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


