import numpy as np

def combine_features(objects, probability = False):
	""" Compiles dictionary objects in to a numpy array suitable for numerical analysis.

	Parameters
	----------
	objects:

	Returns
	-------
	features and respective variables
	"""
	if type(objects) is not list:
		raise Exception("Invalid input to method. Only provide a list object.")

	variables_set = set()
	for object_instance in objects:
		variables_set.update(object_instance.keys())
	variables = list(variables_set)

	features = np.zeros((len(objects), len(variables)))

	for i, object_instance in enumerate(objects):
		for j, variable in enumerate(variables):

			if variable in object_instance.keys():
				features[i, j] = object_instance[variable]

		if probability:
			features[i, :] /= np.sum(features[i, :])



	return features, variables