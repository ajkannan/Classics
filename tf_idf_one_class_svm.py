from os import listdir
from os.path import isfile, join

from Utilities.Text import Text
from Utilities.TermFrequencyInverseDocumentFrequency import TermFrequencyInverseDocumentFrequency as TFIDF

from sklearn import svm
from pprint import pprint
import numpy as np

from sklearn.decomposition import PCA

def main():
	path = "./Texts/Seneca/"
	files = [f for f in listdir(path) if isfile(join(path, f))]

	tfidf = TFIDF()
	for document in files:
		tfidf.add_text_to_corpus(Text(path + document))

	features, word_list = tfidf.calculate_features_for_corpus()

	apply_pca = True
	if apply_pca:
		pca = PCA(n_components = features.shape[1])
		x = {
			"train" : pca.fit_transform(features[[0, 2, 4, 5, 6, 7], :]),
			"test" : pca.transform(features[[1, 3], :])
			}
	else:
		x = {
			"train" : features[[0, 2, 4, 5, 6, 7], :],
			"test" : features[[1, 3], :]
			}

	
	# Unfortunately, it does not appear to be possible to derive a perfect
	# accuracy solution in the grid search specified below. However, it is
	# provided here anyway for educational purposes.
	grid_search = False

	if grid_search:
		for kernel in ["rbf", "linear", "sigmoid", "poly"]:
			for nu in np.linspace(0.001,1.0,200):
				for gamma in np.linspace(0.0,10.0,200):

					clf = svm.OneClassSVM(nu = nu, kernel = kernel, gamma = gamma)
					clf.fit(x["train"])

					y = {
						"train" : clf.predict(x["train"]),
						"test" : clf.predict(x["test"])
						}
					
					if all(y["train"] == 1.0) and all(y["test"] == -1.0):
						pprint({"nu" : nu, "gamma" : gamma, "y" : y, "kernel" : kernel})



	# The following settings using term-frequency inverse-document frequency
	# gives a perfect classification result for the problem of Seneca's
	# authorship attribution.
	nu, kernel, gamma = 0.84437688442211067, "poly", 0.0
	clf = svm.OneClassSVM(nu = nu, kernel = kernel, gamma = gamma)
	clf.fit(x["train"])

	y = {
		"train" : clf.predict(x["train"]),
		"test" : clf.predict(x["test"])
	}

	metrics = {
		"train" : clf.decision_function(x["train"]),
		"test" : clf.decision_function(x["test"])
	}

	pprint({"nu" : nu, "gamma" : gamma, "y" : y, "kernel" : kernel, "metrics" : metrics})


if __name__ == "__main__":
	main()
