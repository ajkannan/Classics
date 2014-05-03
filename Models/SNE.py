import numpy as np
from sklearn.decomposition import PCA

EPSILON = np.finfo(float).eps

def _compute_perplexity(D, precision = 1.0):
	"""Compute the perplexity and the P-row for a specific value of the precision of a Gaussian distribution."""

	perplexity = np.exp(-D.copy() * precision)
	sum_perplexity = np.sum(perplexity)


	if sum_perplexity < EPSILON:
		sum_perplexity = EPSILON

	kernel = np.log(sum_perplexity) + precision * np.sum(D * perplexity) / sum_perplexity
	perplexity /= sum_perplexity
	return kernel, perplexity
	
	
def _data_to_probability(X, tol = 1e-5, perplexity = 30.0):
	"""Performs a binary search to get probability-values in such a way that each conditional Gaussian has the same perplexity."""

	n, d = X.shape
	sum_X = np.sum(np.square(X), axis = 1)
	distances = np.add(np.add(-2 * np.dot(X, X.T), sum_X).T, sum_X)
	probability = np.zeros((n, n))
	precision = np.ones((n, 1))
	entropy = np.log(perplexity)
    
	for i in xrange(n):	
		precision_minimum = -np.inf 
		precision_maximum =  np.inf
		distancesi = distances[i, np.concatenate((np.r_[0:i], np.r_[i + 1:n]))]
		kernel, current_entropy = _compute_perplexity(distancesi, precision[i])
			
		
		kernel_difference = kernel - entropy
		attempts = 0
		while np.abs(kernel_difference) > tol and attempts < 50:
			
			if kernel_difference > 0:
				precision_minimum = precision[i]
				if precision_maximum == np.inf or precision_maximum == -np.inf:
					precision[i] = precision[i] * 2
				else:
					precision[i] = (precision[i] + precision_maximum) / 2
			else:
				precision_maximum = precision[i]
				if precision_minimum == np.inf or precision_minimum == -np.inf:
					precision[i] = precision[i] / 2
				else:
					precision[i] = (precision[i] + precision_minimum) / 2
			
			kernel, current_entropy = _compute_perplexity(distancesi, precision[i])
			kernel_difference = kernel - entropy
			attempts += 1
			
		probability[i, np.concatenate((np.r_[0:i], np.r_[i + 1:n]))] = current_entropy
	
	return probability


class tSNE(object):
	"""docstring for tSNE"""
	def __init__(self, dimensions = 2, apply_pca = True):
		super(tSNE, self).__init__()
		if dimensions != 2 and dimensions != 3:
			raise ValueError("The visualization at dimensions greater other than 2 or 3 are not supported")


		self.dimensions = dimensions
		self.apply_pca = apply_pca
	

	def transform(self, X, initial_dimensions = 50, perplexity = 20.0, max_iterations = 1000):
		if self.apply_pca:
			pca = PCA(n_components = initial_dimensions)
			X = pca.fit_transform(X)

		n, d = X.shape

		momentum = 0.5
		final_momentum = 0.8
		eta = 500
		minimum_gain = 0.01

		projection = np.random.randn(n, self.dimensions)
		dprojection = np.zeros((n, self.dimensions))
		iprojection = np.zeros((n, self.dimensions))
		gains = np.ones((n, self.dimensions))

		probability = _data_to_probability(X, 1e-5, perplexity)
		probability = probability + probability.T
		probability = probability / np.sum(probability)
		probability = probability * 4									
		probability = np.maximum(probability, 1e-12)
		
		for i in xrange(max_iterations):
			sum_Y = np.sum(np.square(projection), axis = 1)		
			num = 1 / (1 + np.add(np.add(-2 * np.dot(projection, projection.T), sum_Y).T, sum_Y))
			num[range(n), range(n)] = 0

			Q = num / np.sum(num)
			Q = np.maximum(Q, 1e-12)
			
			L = (probability - Q) * num
			dprojection = 4 * np.dot((np.diag(np.sum(L, axis = 0)) - L), projection)
						
			if i == 250:
				momentum = final_momentum

			gains = (gains + 0.2) * ((dprojection > 0) != (iprojection > 0)) + (gains * 0.8) * ((dprojection > 0) == (iprojection > 0))
			gains[gains < minimum_gain] = minimum_gain
			iprojection = momentum * iprojection - eta * (gains * dprojection)
			projection += iprojection
			projection -= np.tile(np.mean(projection, 0), (n, 1))
			
			if (i + 1) % 10 == 0:
				C = np.sum(probability * np.log(probability / Q))
			
		
			if i == 100:
				probability /= 4.0
	
		return projection




	