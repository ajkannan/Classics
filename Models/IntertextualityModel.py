from Utilities.Text import Text
from Utilities.FunctionalNGram import FunctionalNGram as FNG
from Utilities.TreeTagger import TreeTagger as POS
from Utilities.combine_features import combine_features as combine

from Models.Metrics import PseudoMetrics

import numpy as np
from matplotlib import pyplot as pl
from operator import itemgetter
from pprint import pprint


class IntertextualityDocumentComparison(object):
	"""docstring for IntertextualityDocumentComparison"""
	def __init__(self, document, query_document, minimum_passage_length, maximum_passage_length,
		step_size, n_passages, representation_type):
		super(IntertextualityDocumentComparisonEquidistance, self).__init__()

		self.document = document
		self.query_document = query_document


		self.maximum_passage_length = maximum_passage_length
		self.minimum_passage_length = minimum_passage_length
		self.step_size = step_size
		self.n_passages = n_passages
		self.representation_type = representation_type


		self.compare_documents_for_intertextuality()

	def compare_documents_for_intertextuality(self):
		discovered_intertextuality = {}
		representation = {
							"FNG" : IntertextualityPassageFNG,
							"POS" : IntertextualityPassagePOS,
			}.get(self.representation_type, IntertextualityPassageFNG)

		for i, length in enumerate(range(self.minimum_passage_length, self.maximum_passage_length, self.step_size)):
			results = []
			passages = self.select_passages_for_comparison(length)

			for passage in passages:
				intertext = representation(passage, self.query_document)
				if len(intertext.intertextual_passages) > 0:
					results.append((passage.concatenated_text, intertext.intertextual_proportion, intertext.intertextual_passages))
			
			if len(results) > 0:
				discovered_intertextuality[length] = results


		self.discovered_intertextuality = discovered_intertextuality
		

class IntertextualityDocumentComparisonEquidistance(IntertextualityDocumentComparison):
	"""docstring for IntertextualityDocumentComparisonEquidistance"""
	def __init__(self, document, query_document, minimum_passage_length = 50, maximum_passage_length = 251,
		step_size = 20, n_passages = 400, representation_type = "FNG"):
		super(IntertextualityDocumentComparisonEquidistance, self).__init__(document, query_document, minimum_passage_length, 
			maximum_passage_length, step_size, n_passages, representation_type)


	def select_passages_for_comparison(self, passage_length):
		passages = []
		sampling_distance = int(np.floor((len(self.document.concatenated_text) - passage_length + 1) / self.n_passages))

		indices = range(0, len(self.document.concatenated_text) - passage_length + 1, sampling_distance)

		for index in indices: 
			passages.append(Text(self.document.concatenated_text[index:index + passage_length]))

			print "Choosing substring in queried document starting at index " + str(index)

		return passages


class IntertextualityDocumentComparisonKannan(object):
	"""docstring for IntertextualityDocumentComparisonKannan"""
	def __init__(self, document, query_document, minimum_passage_length = 50, maximum_passage_length = 251,
		step_size = 20, n_passages = 400, representation_type = "FNG"):
		super(IntertextualityDocumentComparisonEquidistance, self).__init__(document, query_document, minimum_passage_length, 
			maximum_passage_length, step_size, n_passages, representation_type)


	def select_passages_for_comparison(self, passage_length):
		pass



class IntertextualityPassage(object):
	"""docstring for IntertextualityPassage"""
	def __init__(self, passage, query_text, representation):
		super(IntertextualityPassage, self).__init__()

		if type(passage) is not Text or type(query_text) is not Text:
			raise Exception("The input to the IntertextualityPassage class must be provided as Text-type data structures.")

		self.passage = representation(passage)

		self.query_text = query_text
		self.substring_length = len(passage.concatenated_text)

		self.calculate_brofos_kannan_shu_bound()
		self.compare_substrings_to_passage(representation)

	def calculate_brofos_kannan_shu_bound(self, epsilon = 0.1):
		alpha = 0.0001
		b = np.floor(np.log(2.0 / alpha) / (2.0 * epsilon ** 2.0))

		# Avoid flooring to make sure passages at the end of the document get chosen with equal
		# probability
		self.sampling_distance = int(np.floor((len(self.query_text.concatenated_text) - self.substring_length + 1) / b))
		#self.sampling_distance = int(np.floor(len(self.query_text.concatenated_text) / b))

		print "Sampling distance: " + str(self.sampling_distance)
		print "Query text length: " + str(len(self.query_text.concatenated_text))

	def calculate_passage_distributions(self):

		# Extract the counts of 2-grams occuring in the target substring of text and
		# be sure to normalize those counts into a proper probability distribution.
		# The chosen pseudo-metric is only valid when applied to probability distributions.
		self.passage_distribution = self.passage.features.values()
		self.passage_distribution /= np.sum(self.passage_distribution)

	def compare_substrings_to_passage(self, representation, threshold = None):
		# Instantiate an instance of the pseudo metrics class. The Bhattacharyya
		# Distance is considered a "pseudo-metric" because it does not actually
		# obey the triangle inequality.
		pm = PseudoMetrics()
		query_text = self.query_text.concatenated_text


		r = range(0, len(query_text) - self.substring_length, self.sampling_distance)
		bhattacharyya_score = {}




		for i, index in enumerate(r):
			# For every substring in the text, we extract the substring of appropriate length
			# beginning at the ith position.
			query_passage = representation(Text(query_text[index:index + self.substring_length]))

			# We normalize as usual. See above comment.
			distributions, variables = combine([self.passage.features, query_passage.features], probability = True)

			# And finally we calculate the Bhattacharyya Distance by measuring the degree of
			# similarity between the 2-gram probability distribution over both the target
			# sequence and the recently-extracted sequence. For the Bhattacharyya Distance,
			# lower value implies higher similarity.
			bhattacharyya_score[i] = (query_text[index:index + self.substring_length],
				pm.bhattacharyya_distance(distributions[0, :], distributions[1, :]), index)


		scores = np.array([score[1] for score in bhattacharyya_score.values()])
		deviation = np.std(scores)
		average = np.mean(scores)

		if threshold is None:
			threshold = 0.5

		intertextual_passages = [score for score in bhattacharyya_score.values() if score[1] < threshold]
		sorted(intertextual_passages, key = itemgetter(2))
		
		# Iterate through the intertextual passages to weed out inadmissible intertextuality
		# Any overlapping indices are considered inadmissible
		i = 1
		while i < len(intertextual_passages):
			if intertextual_passages[i - 1][2] + self.substring_length > intertextual_passages[i][2]:
				# There is overlap, so we must remove the entry that has the higher Bhattacharyya distance
				if intertextual_passages[i - 1][1] > intertextual_passages[i][1]:
					# Remove the first occurence
					intertextual_passages.pop(i - 1)
				else:
					# Remove the second occurence
					intertextual_passages.pop(i)
			else:
				i += 1

		self.intertextual_proportion = len(intertextual_passages) / float(len(r))
		self.bhattacharyya_score = bhattacharyya_score
		self.intertextual_passages = intertextual_passages


class IntertextualityPassagePOS(IntertextualityPassage):
	"""docstring for IntertextualityPassagePOS"""
	def __init__(self, passage, query_text):
		super(IntertextualityPassagePOS, self).__init__(passage, query_text, POS)


class IntertextualityPassageFNG(IntertextualityPassage):
	"""docstring for IntertextualityPassageFNG"""
	def __init__(self, passage, query_text):
		super(IntertextualityPassageFNG, self).__init__(passage, query_text, FNG)



if __name__ == "__main__":
	document = Text("Tests/jfk_complete.txt")
	document_queried = Text("Tests/jfk_intertextuality.txt")
	test = IntertextualityDocumentComparisonEquidistance(document, document_queried)
	pprint(test.discovered_intertextuality)




