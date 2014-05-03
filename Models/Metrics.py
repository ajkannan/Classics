import numpy as np

class Kernel(object):
	"""docstring for Kernel"""
	def __init__(self, kernel, sigma = 5.0):
		super(Kernel, self).__init__()
		self.kernel = {
					  "rbf" : self.radial_basis,
					  "linear" : self.linear,
					  "polynomial" : self.polynomial
					  }.get(kernel, "rbf")

		self.sigma = sigma


	def construct_gramian_matrix(self, X):
		n, m = X.shape
		K = np.zeros((n, n))

		for i in range(n):
			for j in range(n):
				K[i, j] = self.kernel(X[i, :], X[j, :])

		return K

	def evaluate_kernel(self, X, x):
		n = X.shape[0]
		K = np.zeros((n, 1))

		for i in range(n):
			K[i] = self.kernel(x, X[i, :])

		return K

	def linear(self, x, y):
		return np.dot(x, y)

	def polynomial(self, x, y):
		return (1.0 + np.dot(x, y)) ** self.sigma

	def radial_basis(self, x, y):
		return np.exp(-np.linalg.norm(x - y) ** 2.0 / (2.0 * (self.sigma ** 2.0)))
	

class PseudoMetrics(object):
	"""docstring for PseudoMetrics"""
	def __init__(self):
		super(PseudoMetrics, self).__init__()


	def bhattacharyya_distance(self, p, q):
		# The Bhattacharyya coefficient.
		bc = np.sum(np.sqrt(p * q))

		# The Bhattacharyya distance.
		bd = -np.log(bc)
		return bd if not np.isinf(bd) else np.nan
	