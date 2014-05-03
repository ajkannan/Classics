from pprint import pprint, pformat
import codecs

class Dictionary(object):

	def __init__(self):
		super(Dictionary, self).__init__()
		self.parse_dictionary()

		#for key in latin_dictionary:
		#	print key, latin_dictionary[key], check_for_long_vowels(key, latin_dictionary)


	def parse_dictionary(self):
		latin_dictionary = {}
		with codecs.open('Texts/Dictionary/latin_dictionary.xml', encoding='utf-8') as f:
			saved_key = None
			for line in f:
				if "<entry id=" in line:
					key_start = line.index('key="') + 5
					key_end = line[key_start:].index('"') + key_start
					key = line[key_start:key_end]
					if key[-1].isdigit():
						if int(key[-1]) != 1:
							pass # Ignore multiple definitions of a word for now
						key = key[:-1] # Parse out digit at end of word to mark multiple words

					if "<orth" in line:
						word_start = line[line.index("<orth"):].index(">") + 1 + len(line[:line.index("<orth")])
						word_end = line.index("</orth>")
						word = line[word_start:word_end]
						latin_dictionary[key] = self.prune_word(key, word)
					else:
						saved_key = key

				elif "<orth" in line:
					word_start = line[line.index("<orth"):].index(">") + 1 + len(line[:line.index("<orth")])
					word_end = line.find("</orth>")
					word = line[word_start:word_end]
					latin_dictionary[saved_key] = self.prune_word(saved_key, word)

		f.close()
		self.latin_dictionary = latin_dictionary


	def prune_word(self, key, word):
		if '-' in word and '-' not in key:
			word = word[:word.index('-')] + word[word.index('-') + 1:]

		if len(word) > len(key):
			if '(' in word:
				if word.index('(') == 0:
					word = word[1:-1]
					'''if ')' in word:
						word = word[:word.index(')')]'''
				else:
					word = word[:word.index('(')]

			word = word.strip()
			if ',' in word:
				word = word[:word.index(',')]
			if ' ' in word and len(word[:word.index(' ')]) >= len(key):
				word = word[:word.index(' ')]

		word = word.replace(' ', '')

		return word


	def find_long_vowels(self, keyword):
		if keyword in self.latin_dictionary:
			# Return indices of long vowels
			word = self.latin_dictionary[keyword]
			non_ascii_indices = [i for i in xrange(min(len(keyword),len(word))) if ord(word[i]) > ord('z')]
			return non_ascii_indices
		else:
			return [-1]




