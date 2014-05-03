from Models.OneClassSVM import OneClassSVM as SVM

from os import listdir
from os.path import isfile, join
from pprint import pprint

from Utilities.Text import Text
from Utilities.FunctionalNGram import FunctionalNGram as FNG
from Utilities.FunctionalNGram import combine_n_gram_features as combine

import pylab as pl
import matplotlib.font_manager
import numpy as np

def main():
	xx, yy = np.meshgrid(np.linspace(-5, 5, 10), np.linspace(-5, 5, 10))
	# Generate train data
	X = 0.3 * np.random.randn(100, 2)
	X_train = np.r_[X + 2, X - 2]
	# Generate some regular novel observations
	X = 0.3 * np.random.randn(20, 2)
	X_test = np.r_[X + 2, X - 2]
	# Generate some abnormal novel observations
	X_outliers = np.random.uniform(low=-4, high=4, size=(20, 2))

	# fit the model
	clf = SVM()
	clf.fit(X_train)
	y_pred_train = clf.predict(X_train)
	y_pred_test = clf.predict(X_test)
	y_pred_outliers = clf.predict(X_outliers)
	
	n_error_train = y_pred_train[y_pred_train == -1].size
	n_error_test = y_pred_test[y_pred_test == -1].size
	n_error_outliers = y_pred_outliers[y_pred_outliers == 1].size

	# plot the line, the points, and the nearest vectors to the plane
	Z = clf.decision_function(np.c_[xx.ravel(), yy.ravel()])
	Z = Z.reshape(xx.shape)

	pl.title("Novelty Detection")
	pl.contourf(xx, yy, Z, levels=np.linspace(Z.min(), 0, 7), cmap=pl.cm.Blues_r)
	a = pl.contour(xx, yy, Z, levels=[0], linewidths=2, colors='red')
	pl.contourf(xx, yy, Z, levels=[0, Z.max()], colors='orange')

	b1 = pl.scatter(X_train[:, 0], X_train[:, 1], c='white')
	b2 = pl.scatter(X_test[:, 0], X_test[:, 1], c='green')
	c = pl.scatter(X_outliers[:, 0], X_outliers[:, 1], c='red')
	pl.axis('tight')
	pl.xlim((-5, 5))
	pl.ylim((-5, 5))

	pl.legend([a.collections[0], b1, b2, c],
		["learned frontier", "training observations",
		"new regular observations", "new abnormal observations"],
		loc="upper left",
		prop=matplotlib.font_manager.FontProperties(size=11))
	pl.xlabel(
		"error train: %d/200 ; errors novel regular: %d/20 ; "
		"errors novel abnormal: %d/20" % (n_error_train, n_error_test, n_error_outliers))
	pl.show()

if __name__ == "__main__":
	main()



