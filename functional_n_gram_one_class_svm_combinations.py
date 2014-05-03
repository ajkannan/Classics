from os import listdir
from os.path import isfile, join
import itertools

from Utilities.Text import Text
from Utilities.FunctionalNGram import FunctionalNGram as FNG
from Utilities.TermFrequencyInverseDocumentFrequency import TermFrequencyInverseDocumentFrequency as TFIDF
from Utilities.combine_features import combine_features as combine

from sklearn import svm
from sklearn import preprocessing
from sklearn.decomposition import PCA

from pprint import pprint
import numpy as np



def main():
	path = "./Texts/Seneca/"
	files = [f for f in listdir(path) if isfile(join(path, f))]
	pprint(files)
	frauds = ["octavia.txt", "hercules_oetaeus.txt"]
	#frauds = ["jfk.txt", "medea.txt"]
	fraud_indices = np.array([files.index(f) for f in frauds])


	tfidf = TFIDF()
	for document in files:
		tfidf.add_text_to_corpus(Text(path + document))

	tfidf_features, word_list = tfidf.calculate_features_for_corpus()
	n_documents = tfidf_features.shape[0]
	legitimate_indices = np.array(list(set(range(n_documents)) - set(fraud_indices)))


	fng_features, n_grams = combine([FNG(Text(path + f)).probability_features for f in files])


	features = np.hstack((fng_features, tfidf_features))




	x = {
		"train" : features[legitimate_indices, :],
		"test" : features[fraud_indices, :]
		}
	
	files.pop(max(fraud_indices))
	files.pop(min(fraud_indices))




	indices = set(range(x["train"].shape[0]))
	nu, kernel, gamma = 0.4, "rbf", 0.1
	clf = svm.OneClassSVM(nu = nu, kernel = kernel, gamma = gamma)

	for train_index_set in list(itertools.combinations(list(indices), features.shape[0] - 4)):
		train_index = np.array(list(train_index_set))
		test_index = np.array(list(indices - set(train_index)))
		
		train_data = x["train"][train_index, :]
		test_data = np.append(x["test"], x["train"][test_index, :], axis = 0)

		apply_pca = True
		if apply_pca:
			pca = PCA(n_components = train_data.shape[1])
		
			train_data = pca.fit_transform(train_data)
			test_data = pca.transform(test_data)


		clf.fit(train_data)

		y = {
			# "train" : clf.predict(train_data),
			"test" : clf.predict(test_data)
		}

		metrics = {
			# "train" : clf.decision_function(train_data),
			"test" : clf.decision_function(test_data)
		}

		results = {"files" : {"train" : [files[index] for index in train_index], "test" : [files[index] for index in test_index]},"nu" : nu, "gamma" : gamma, "y" : y, "kernel" : kernel, "metrics" : metrics}

		pprint(results)
		print


	print
	print "Results from all data:"

	clf.fit(x["train"])

	y = {
		# "train" : clf.predict(x["train"]),
		"test" : clf.predict(x["test"])
	}

	metrics = {
		# "train" : clf.decision_function(x["train"]),
		"test" : clf.decision_function(x["test"])
	}

	pprint({"nu" : nu, "gamma" : gamma, "y" : y, "kernel" : kernel, "metrics" : metrics})



if __name__ == "__main__":
	main()

