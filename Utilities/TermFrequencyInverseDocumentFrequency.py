from Text import Text
from Dictionary import Dictionary

from pprint import pprint
import urllib2

import numpy as np

class TermFrequencyInverseDocumentFrequency(object):
	"""docstring for TermFrequencyInverseDocumentFrequency"""
	def __init__(self):
		super(TermFrequencyInverseDocumentFrequency, self).__init__()
		
		self.corpus = []
		self.corpus_frequencies = {}

		
	def add_text_to_corpus(self, text):
		text_word_list = text.list
		#####text_frequencies = self.calculate_normalized_frequencies(text_word_list)
		text_frequencies = self.calculate_normalized_frequencies(text_word_list[:200])
		
		self.corpus.append((text.name, text_frequencies))


	def calculate_normalized_frequencies(self, text_word_list, add_text = True):
		text_frequencies = {}
		length = float(len(text_word_list))

		base_words = {}
		latin_words = Dictionary().latin_dictionary

		#####for word in text_word_list:
		for word in text_word_list[:200]:
			if word not in latin_words and word not in base_words:
				# Look up the word in the Perseus project
				word_url = 'http://www.perseus.tufts.edu/hopper/morph?l=' + word + '&la=la'
				try:
					morphology_raw = urllib2.urlopen(word_url).read()
					print word
					start_index = morphology_raw.index('<h4 class="la">') + 15
					end_index = morphology_raw.index('</h4>', start_index)
					morphology = morphology_raw[start_index:end_index]
					base_words[word] = morphology
					word = morphology
				except:
					pass
			elif word in base_words:
				word = base_words[word]
			text_frequencies[word] = text_frequencies.get(word, 0.0) + 1.0
	

			if add_text:
				self.corpus_frequencies[word] = self.corpus_frequencies.get(word, 0.0) + 1.0

		for word in text_frequencies.keys():
			text_frequencies[word] /= length

		return text_frequencies


	'''def calculate_normalized_frequencies(self, text_word_list, add_text = True):
		text_frequencies = {}
		length = float(len(text_word_list))

		for word in text_word_list:
			text_frequencies[word] = text_frequencies.get(word, 0.0) + 1.0
	
			if add_text:
				self.corpus_frequencies[word] = self.corpus_frequencies.get(word, 0.0) + 1.0

		for word in text_frequencies.keys():
			text_frequencies[word] /= length

		return text_frequencies'''

	def calculate_similarity_scores(self, text):
		query_text_frequencies = self.calculate_normalized_frequencies(text.list, add_text = False)

		similarities = []

		for document in self.corpus:
			similarity_score = 0.0

			document_frequencies = document[1]

			for word in query_text_frequencies.keys():

				if word in document_frequencies.keys():
					similarity_score += (query_text_frequencies[word] / self.corpus_frequencies[word]) + (
						document_frequencies[word] / self.corpus_frequencies[word]
						)

			similarities.append((document[0], similarity_score))

			return similarities

	def calculate_features_for_corpus(self):		
		features = np.zeros((len(self.corpus), len(self.corpus_frequencies.keys())))
		
		for i, document in enumerate(self.corpus):
			for j, word in enumerate(self.corpus_frequencies.keys()):

				if word in document[1].keys():
					features[i, j] = document[1][word]
				else:
					features[i, j] = 0.0

		return features, self.corpus_frequencies.keys()

