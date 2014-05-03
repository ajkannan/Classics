from Text import Text
from Text import GreekText

from pprint import pprint
import numpy as np
import string
import itertools
from copy import copy






class FunctionalNGram(object):
	""" Represents the functional n-gram feature representation of the text"""
	def __init__(self, text, n = 2):
		""" Calls functions to calculate probabilities of n-grams

		Parameters
		----------
		n: size of lettergram

		Returns
		-------
		None
		"""

		super(FunctionalNGram, self).__init__()

		# if type(text) is not Text:
		# 	raise Exception("Invalid input to FunctionalNGram class. Only provide inputs of type Text.")

		self.text = text
		self.find_n_grams(n)
		self.compute_probability_features()


	def find_n_grams(self, n):
		""" Iterates through text finding frequencies of n-grams

		Parameters
		----------
		n: size of lettergram

		Returns
		-------
		None
		"""

		n_grams = self.initialize_n_grams(n)
		text = self.text.processed_text

		for line in text:
			joined_line = " ".join(line)
			for i in xrange(len(joined_line) - n + 1):
				n_gram = tuple([joined_line[i + j] for j in xrange(n)])
				if n_gram in n_grams.keys():
					n_grams[n_gram] += 1.0

		self.features = n_grams


	def initialize_n_grams(self, n):
		""" Initializes n-gram dictionary.

		Keys of the dictionary are all possible n-grams of alphabetical letters
		and spaces (punctuation not included). Values in the dictionary are the
		respective frequencies.

		Parameters
		----------
		n: size of lettergram

		Returns
		-------
		dictionary mentioned above
		"""

		n_grams = {}
		keys = []
		letters = " " + string.ascii_lowercase
		for letter_1 in letters:
			keys.append([letter_1])

		for i in xrange(1, n):
			# Add next character to each key
			keys_copy = copy(keys)

			for key in keys_copy:
				for letter in letters:
					new_key = copy(key)
					new_key.append(letter)
					keys.append(new_key)

			# Remove shorter keys
			keys_copy = copy(keys)

			for key in keys_copy:
				if len(key) < i + 1:
					keys.remove(key)

		for key in keys:
			n_grams[tuple(key)] = 0.0

		return n_grams


	def compute_probability_features(self):
		""" Computes probability features

		Parameters
		----------
		None

		Returns
		-------
		None
		"""

		n_gram_tuples = self.features.keys()
		n_gram_probabilities = {}
		alphabet = {}

		n_gram_buckets = {}
		for n_gram in n_gram_tuples:
			if n_gram[:-1] in n_gram_buckets:
				n_gram_buckets[n_gram[:-1]].add(n_gram)
			else:
				n_gram_buckets[n_gram[:-1]] = set([n_gram])

		for n_gram_beginning in n_gram_buckets.keys():
			frequency_count = 0.0
			for n_gram in n_gram_buckets[n_gram_beginning]:
				frequency_count += self.features[n_gram]

			alphabet[n_gram[:-1]] = frequency_count

		for key in alphabet.keys():
			for n_gram in n_gram_buckets[key]:
				if alphabet[key] == 0.0:
					n_gram_probabilities[n_gram] = 0.0
				else:
					n_gram_probabilities[n_gram] = self.features[n_gram] / alphabet[key]


		self.probability_features = n_gram_probabilities



class GreekFunctionalNGram(FunctionalNGram):
	"""docstring for GreekFunctionalNGram"""
	def __init__(self, text, n = 2):
		super(GreekFunctionalNGram, self).__init__(text, n)
		
		# if type(text) is not GreekText:
		# 	raise Exception("Invalid input to GreekFunctionalNGram class. Only provide inputs of type GreekText.")


	def find_n_grams(self, n):
		n_grams = self.initialize_n_grams(n) 
		# print n_grams
		
		text = self.text.character_list 
 
		for i in xrange(len(text)): 
			n_gram = tuple(text[i:i + n])
			# print n_gram
			if n_gram in n_grams.keys(): 
				n_grams[n_gram] += 1.0 
 
		self.features = n_grams

	def initialize_n_grams(self, n):
		
		character_set = set(self.text.character_list)

		# print list(character_set)
		# print list(itertools.combinations(character_set, 2))

		character_n_grams = list(itertools.combinations(character_set, n))
		n_grams = {}
		for n_gram in character_n_grams:
			n_grams[n_gram] = 0.0

		return n_grams



