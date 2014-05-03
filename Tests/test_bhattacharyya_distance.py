import numpy as np
from matplotlib import pyplot as pl

from Models.Metrics import PseudoMetrics
from Utilities.FunctionalNGram import FunctionalNGram as FNG
from Utilities.Text import Text

from pprint import pprint

def main():
	
	# Instantiate an instance of the pseudo metrics class. The Bhattacharyya
	# Distance is considered a "pseudo-metric" because it does not actually
	# obey the triangle inequality.
	pm = PseudoMetrics()

	# Read text from file. We are using toy data here, so we only read an example
	# of Lorem Ipsum (appropriately enough, it's Latin).
	with open("Tests/lorem_ipsum.txt", "r") as f:
		for line in f:
			text = line

	# Define a substring length to consider. We will query the text for strings of
	# text that are roughly similar to a particular substring according to the 
	# Bhattacharyya Distance of their 2-gram probability distributions.
	substring_length = 50
	target_text = Text(text[32:32 + substring_length])
	target = FNG(target_text)

	# Extract the counts of 2-grams occuring in the target substring of text and
	# be sure to normalize those counts into a proper probability distribution. 
	# The chosen pseudo-metric is only valid when applied to probability distributions.
	target_distribution = target.n_grams.values()
	target_distribution /= np.sum(target_distribution)

	bhattacharyya_score = np.zeros((len(text) - substring_length, 1))

	for i in range(len(text) - substring_length):
		# For every substring in the text, we extract the substring of appropriate length
		# beginning at the ith position.
		query_text = FNG(Text(text[i:i + substring_length]))

		# We normalize as usual. See above comment.
		query_distribution = query_text.n_grams.values()
		query_distribution /= np.sum(query_distribution)

		# And finally we calculate the Bhattacharyya Distance by measuring the degree of 
		# similarity between the 2-gram probability distribution over both the target 
		# sequence and the recently-extracted sequence. For the Bhattacharyya Distance,
		# lower value implies higher similarity.
		bhattacharyya_score[i] = pm.bhattacharyya_distance(target_distribution, query_distribution)

	# Find the substring index with the highest similarity.
	minimum_index = bhattacharyya_score.argmin()

	pl.plot(np.arange(len(text) - substring_length), bhattacharyya_score, "k--", label = u"Bhattacharyya Score per Substring")
	pl.plot(minimum_index, bhattacharyya_score.min(), "r.", markersize = 10, label = u"Most Similar Substring")
	pl.text(minimum_index + .1, bhattacharyya_score.min() - .1, text[minimum_index:minimum_index + substring_length])

	pl.xlabel("Index of substring beginning (substring length $" + str(substring_length) + "$)")
	pl.ylabel("Bhattacharyya Score")
	pl.title("Bhattacharyya Distance for Similarity Matching")
	pl.legend(loc = "upper left")
	pl.axis([0, len(text) - substring_length, -0.5, 2.5])
	pl.show()


if __name__ == "__main__":
	main()