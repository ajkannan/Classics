
from pprint import pprint
import re
import string

from os.path import split, exists


class Text(object):
	""" The Text class represents the text in different formats.

	The functions within this class clean up the raw representation of text and
	allow for manipulation of word case and punctuation. """
	
	def __init__(self, document):
		""" Calls functions to preprocess raw text

		Parameters
		----------
		document: the file path to the file containing the raw text, or the plain
				  text string containing the document.

		Returns
		-------
		None """

		super(Text, self).__init__()

		if exists(document):
			self.open_file_path(document)
			self.name = split(document)[-1]
		else:
			self.raw = [document]
			self.name = "Unknown"


		self.preprocess_raw_text()
		self.concatenate_processed_text()
		self.generate_list_of_words()

		

	def open_file_path(self, file_path):
		""" Opens the desire file and obtains raw text as a single string.

		Parameters
		----------
		file_path: the file path to the file containing the raw text

		Returns
		-------
		None """

		text = []
		with open(file_path, "r") as f:
			for line in f:
				text.append(line)

		self.raw = text

	def preprocess_raw_text(self, lower_case = True, punctuation = "delete"):
		""" Parses entire raw text line by line.

		Splits raw text into lines and calls helper function to process each line.

		Parameters
		----------
		lower_case: True makes all words lowercase, False leaves capitalization
		            as is (True by default)
		punctuation: "separate" will separate punctuation from the neighboring words
	                 "delete" will delete all punctuation
					 Anything else will leave the punctuation as is, which most
					 often means the punctuation will be the last character of
					 the preceding word in the line of text.
					 ("delete" is default)
		Returns
		-------
		None
		"""


		processed_text = []
		for line in self.raw:
			processed_line = self.process_line(line, lower_case, punctuation)
			if len(processed_line):
				processed_text.append(processed_line)

		self.processed_text = processed_text

	def process_line(self, line, lower_case, punctuation):
		""" Processes a single line of the text.

		This function removes numbers and speaker names from the line, processes
		punctuation, and makes all words lower case if desired.

		Notes:
		-Speaker names are identified by [SPEAKER].  If the brackets are
		not present, then speaker names will not be removed.

		Parameters
		----------
		line: a single line of text from the raw input string
		lower_case: boolean (True makes words lower case, False leaves
		            capitalization as is
		punctuation: "separate" will separate punctuation from the neighboring words
	                 "delete" will delete all punctuation
					 Anything else will leave the punctuation as is, which most
					 often means the punctuation will be the last character of
					 the preceding word in the line of text.

		Returns
		-------
		None
		"""

		# Removes line numbers and other numeric strings from this line of
		# the play.
		processed_line = [word for word in line.split() if not word.isdigit()]


		# Removes the speaker indicator from this particular line. Speakers are
		# indicated by the convention "[SPEAKER]". If the option is specified as
		# True, then these remaining words are also converted to their lower 
		# case form in this step.
		processed_line = [word.lower() if lower_case else word for word in processed_line if word[0] != "[" and word[-1] != "]"]

	
		if punctuation == "separate":
			# In the event that we wish to separate punctuation from neighboring 
			# words, then we employ the regular expression tool to create the 
			# separated list.
			processed_line = re.findall(u"[\w']+|[.,!?;]", " ".join(processed_line))

		elif punctuation == "delete":
			# In the event that we wish to delete punctation from the text, 
			# we employ the regular expressions tool to separate punctuation and 
			# subsequently remove punctuation from the resulting list.
			punctuation_set = set([".", ",", "!", "?", ";"])

			separated_punctuation = re.findall(u"[\w']+|[.,!?;]", " ".join(processed_line))
			punctuation_removed = ["".join(c for c in s if c not in punctuation_set) for s in separated_punctuation]
			processed_line = [word for word in punctuation_removed if word != ""]

		return processed_line

	def concatenate_processed_text(self):
		""" Transforms list of lines of processed text into one large string.

		Parameters
		----------
		None

		Returns
		-------
		None """


		concatenated_text = ""
		for line in self.processed_text:
			concatenated_text += " ".join(line) + " "


		# Remove the trailing space character from the concatenated string
		# of words.
		concatenated_text = concatenated_text[:-1]

		self.concatenated_text = concatenated_text

	def generate_list_of_words(self):
		self.list = self.concatenated_text.split()

class GreekText(Text):
	"""docstring for GreekText"""
	def __init__(self, document):
		super(GreekText, self).__init__(document)
		self.generate_character_list()
	
	def process_line(self, line, lower_case, punctuation):
		processed_line = line
		punctuation_set = set([";", ".", "?", ":", ",", "!", "\n", "\r", "\xe2\x80\x94", "\x80\xa0"])
		for punctation in punctuation_set:
			processed_line = processed_line.replace(punctation, "")

		# Removes line numbers and other numeric strings from this line of
		# the play.
		processed_line = [word for word in processed_line.split() if not word.isdigit()]


		# Removes the speaker indicator from this particular line. Speakers are
		# indicated by the convention "[SPEAKER]". If the option is specified as
		# True, then these remaining words are also converted to their lower 
		# case form in this step.
		processed_line = [word.lower() if lower_case else word for word in processed_line]

		# print processed_line

		if len(processed_line):
			if processed_line[0][0] == "*" and len(processed_line) == 1:
				processed_line = []
			for i, word in enumerate(processed_line):
				processed_line[i] = word.replace("*", "")
		
		# print processed_line
		# print self.strip_non_ascii(processed_line)

		return self.strip_non_ascii(processed_line)

	def strip_non_ascii(self, string):
		line = []
		for word in string:
			stripped = (c for c in word if 0 < ord(c) < 127)
			line.append("".join(stripped))

		return line

	def generate_character_list(self):
		characters = []
		alphabet = string.ascii_lowercase + " "

		for character in self.concatenated_text:
			# print characters
			if len(characters) == 0:
				characters.append(character)
			elif character in alphabet or characters[-1] == " ":
				characters.append(character)
			else:
				characters[-1] += character

		self.character_list = characters





