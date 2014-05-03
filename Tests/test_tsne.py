from os import listdir
from os.path import isfile, join


import numpy as np
import pylab as pl

from Utilities.FunctionalNGram import FunctionalNGram as FNG
from Utilities.TreeTagger import TreeTagger as TT
from Utilities.Text import Text
from Utilities.combine_features import combine_features as combine

from sklearn import svm, preprocessing
from pprint import pprint
import matplotlib.font_manager

EPSILON = np.finfo(float).eps


def Hbeta(D = np.array([]), beta = 1.0):
	"""Compute the perplexity and the P-row for a specific value of the precision of a Gaussian distribution."""
	
	# Compute P-row and corresponding perplexity
	P = np.exp(-D.copy() * beta);
	sumP = np.sum(P);
	if sumP < EPSILON:
		sumP = EPSILON

	H = np.log(sumP) + beta * np.sum(D * P) / sumP;
	P = P / sumP;
	return H, P;
	
	
def x2p(X = np.array([]), tol = 1e-5, perplexity = 30.0):
	"""Performs a binary search to get P-values in such a way that each conditional Gaussian has the same perplexity."""

	# Initialize some variables
	print "Computing pairwise distances..."
	(n, d) = X.shape;
	sum_X = np.sum(np.square(X), 1);
	D = np.add(np.add(-2 * np.dot(X, X.T), sum_X).T, sum_X);
	P = np.zeros((n, n));
	beta = np.ones((n, 1));
	logU = np.log(perplexity);
    
	# Loop over all datapoints
	for i in range(n):
	
		# Print progress
		if i % 500 == 0:
			print "Computing P-values for point ", i, " of ", n, "..."
	
		# Compute the Gaussian kernel and entropy for the current precision
		betamin = -np.inf; 
		betamax =  np.inf;
		Di = D[i, np.concatenate((np.r_[0:i], np.r_[i+1:n]))];
		(H, thisP) = Hbeta(Di, beta[i]);
			
		# Evaluate whether the perplexity is within tolerance
		Hdiff = H - logU;
		tries = 0;
		while np.abs(Hdiff) > tol and tries < 50:
				
			# If not, increase or decrease precision
			if Hdiff > 0:
				betamin = beta[i];
				if betamax == np.inf or betamax == -np.inf:
					beta[i] = beta[i] * 2;
				else:
					beta[i] = (beta[i] + betamax) / 2;
			else:
				betamax = beta[i];
				if betamin == np.inf or betamin == -np.inf:
					beta[i] = beta[i] / 2;
				else:
					beta[i] = (beta[i] + betamin) / 2;
			
			# Recompute the values
			(H, thisP) = Hbeta(Di, beta[i]);
			Hdiff = H - logU;
			tries = tries + 1;
			
		# Set the final row of P
		P[i, np.concatenate((np.r_[0:i], np.r_[i+1:n]))] = thisP;
	
	# Return final P-matrix
	print "Mean value of sigma: ", np.mean(np.sqrt(1 / beta))
	return P;
	
	
def pca(X = np.array([]), no_dims = 50):
	"""Runs PCA on the NxD array X in order to reduce its dimensionality to no_dims dimensions."""

	print "Preprocessing the data using PCA..."
	(n, d) = X.shape;
	X = X - np.tile(np.mean(X, 0), (n, 1));
	(l, M) = np.linalg.eig(np.dot(X.T, X));
	Y = np.dot(X, M[:,0:no_dims]);
	return Y;


def tsne(X = np.array([]), no_dims = 2, initial_dims = 50, perplexity = 30.0):
	"""Runs t-SNE on the dataset in the NxD array X to reduce its dimensionality to no_dims dimensions.
	The syntaxis of the function is Y = tsne.tsne(X, no_dims, perplexity), where X is an NxD NumPy array."""
	
	# Check inputs
	if X.dtype != "float64":
		print "Error: array X should have type float64.";
		return -1;
	#if no_dims.__class__ != "<type 'int'>":			# doesn't work yet!
	#	print "Error: number of dimensions should be an integer.";
	#	return -1;
	
	# Initialize variables
	X = pca(X, initial_dims);
	(n, d) = X.shape;
	max_iter = 1000;
	initial_momentum = 0.5;
	final_momentum = 0.8;
	eta = 500;
	min_gain = 0.01;
	Y = np.random.randn(n, no_dims);
	dY = np.zeros((n, no_dims));
	iY = np.zeros((n, no_dims));
	gains = np.ones((n, no_dims));
	
	# Compute P-values
	P = x2p(X, 1e-5, perplexity);
	P = P + np.transpose(P);
	P = P / np.sum(P);
	P = P * 4;									# early exaggeration
	P = np.maximum(P, 1e-12);
	
	# Run iterations
	for iter in range(max_iter):
		
		# Compute pairwise affinities
		sum_Y = np.sum(np.square(Y), 1);		
		num = 1 / (1 + np.add(np.add(-2 * np.dot(Y, Y.T), sum_Y).T, sum_Y));
		num[range(n), range(n)] = 0;
		Q = num / np.sum(num);
		Q = np.maximum(Q, 1e-12);
		
		# Compute gradient
		PQ = P - Q;
		for i in range(n):
			dY[i,:] = np.sum(np.tile(PQ[:,i] * num[:,i], (no_dims, 1)).T * (Y[i,:] - Y), 0);
			
		# Perform the update
		if iter < 20:
			momentum = initial_momentum
		else:
			momentum = final_momentum
		gains = (gains + 0.2) * ((dY > 0) != (iY > 0)) + (gains * 0.8) * ((dY > 0) == (iY > 0));
		gains[gains < min_gain] = min_gain;
		iY = momentum * iY - eta * (gains * dY);
		Y = Y + iY;
		Y = Y - np.tile(np.mean(Y, 0), (n, 1));
		
		# Compute current value of cost function
		if (iter + 1) % 10 == 0:
			C = np.sum(P * np.log(P / Q));
			print "Iteration ", (iter + 1), ": error is ", C
			
		# Stop lying about P-values
		if iter == 100:
			P = P / 4;
			
	# Return solution
	return Y;
		
	
if __name__ == "__main__":

	path = "./Texts/"
	files = [f for f in listdir(path) if isfile(join(path, f))]

	features, n_grams = combine([TT(Text(path + f)).features for f in files])

	tsne_features = tsne(features, 2, 50, 20.0);
	tsne_features = preprocessing.normalize(tsne_features, norm='l2', axis=1, copy=True)

	seneca = np.array([True, False, True, False, True, True, True, True])
	not_seneca = np.array([False, True, False, True, False, False, False, False])

	nu = 0.2
	gamma = 0.0
	kernel = "rbf"

	clf = svm.OneClassSVM(nu = nu, kernel = kernel, gamma = gamma)
	clf.fit(tsne_features[seneca, :])

	y = {
		"train" : clf.predict(tsne_features[seneca, :]),
		"test" : clf.predict(tsne_features[not_seneca, :])
	}

	metrics = {
		"train" : clf.decision_function(tsne_features[seneca, :]),
		"test" : clf.decision_function(tsne_features[not_seneca, :])
	}

	pprint({"nu" : nu, "gamma" : gamma, "y" : y, "kernel" : kernel, "metrics" : metrics})

	bounds = .1
	xx, yy = np.meshgrid(np.linspace(np.min(tsne_features[:,0]) - bounds, np.max(tsne_features[:,0]) + bounds, 500), 
		np.linspace(np.min(tsne_features[:,1]) - bounds, np.max(tsne_features[:,1]) + bounds, 500))
	Z = clf.decision_function(np.c_[xx.ravel(), yy.ravel()])
	Z = Z.reshape(xx.shape)

	pl.title("Novelty Detection")
	pl.xlabel("First $t$-SNE Dimension")
	pl.ylabel("Second $t$-SNE Dimension")
	pl.contourf(xx, yy, Z, levels=np.linspace(Z.min(), 0, 7), cmap=pl.cm.Blues_r)
	a = pl.contour(xx, yy, Z, levels=[0], linewidths=2, colors='red')
	pl.contourf(xx, yy, Z, levels=[0, Z.max()], colors='orange')
	b1 = pl.scatter(tsne_features[seneca, 0], tsne_features[seneca, 1], c='white')
	b2 = pl.scatter(tsne_features[not_seneca, 0], tsne_features[not_seneca, 1], c='green')
	pl.xlim((xx.min(), xx.max()))
	pl.ylim((yy.min(), yy.max()))	
	pl.legend([a.collections[0], b1, b2], ["Learned Frontier", "Seneca Works", "Works by Others"], 
		loc="upper left", prop=matplotlib.font_manager.FontProperties(size=11))
	pl.show()

