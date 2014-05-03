import numpy as np
from Models.Metrics import Kernel

from pprint import pprint
from cvxopt import matrix, solvers

solvers.options["show_progress"] = False

class OneClassSVM(object):
	"""docstring for OneClassSVM"""
	def __init__(self, kernel = "rbf", nu = 0.1, sigma = 5.0):
		super(OneClassSVM, self).__init__()
		
		self.sigma = sigma
		self.nu = nu

		self.kernel = Kernel(kernel)
		

	def fit(self, X):
		n, m = X.shape

		K = self.kernel.construct_gramian_matrix(X)
		
		P = K
		q = np.zeros((n, 1))
		A = np.ones((1, n))
		b = np.ones((1,1))

		G = np.append(-1.0 * np.identity(n), np.identity(n), axis = 0)
		C = 1.0 / (self.nu * n)
		h = np.zeros((2 * n, 1))
		h[n:] = C

		pprint({"P" : P, "q" : q, "A" : A, "b" : b, "G" : G, "h" : h})

		solution = solvers.qp(matrix(P), matrix(q), matrix(G), matrix(h), matrix(A), matrix(b))

		# Lagrange multipliers.
		a = np.ravel(solution["x"])
		support_vector_indices = a > 1e-5
		rho_index = (i for i, boolean in enumerate(support_vector_indices) if boolean).next()
		
		a = a[support_vector_indices]
		rho = np.sum(a * K[rho_index, support_vector_indices])

		self.a = a
		self.rho = rho
		self.support_vectors = X[support_vector_indices, :]

	def decision_function(self, X):
		return np.array([np.sum(self.a * self.kernel.evaluate_kernel(self.support_vectors, x)) - self.rho for x in X])

	def predict(self, X):
		return np.sign(self.decision_function(X))



