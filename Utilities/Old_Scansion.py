#!/usr/bin/python
# -*- coding: utf-8 -*-

import string
import sys, codecs

from Text import Text
from Dictionary import Dictionary

vowels = set('aeiou')
consonants = set(string.ascii_lowercase) - vowels

class Scansion(object):
	def __init__(self, text):
		super(Scansion, self).__init__()
		self.text = text
		self.scan_text()


	def scan_text(self):
		self.eliminate_elisions()
		self.mark_naturally_long_vowels()
		self.mark_diphthongs()
		self.mark_lengthened_vowels()
		self.mark_last_foot()
		self.mark_remaining_as_short()
		self.pure_scansion()
		self.divide_verse_into_feet()


	def eliminate_elisions(self):
		global vowels
		de_elided_text = self.text.processed_text # Get the line by line text
		for line in de_elided_text:
			for i in xrange(len(line) - 1):
				if ((line[i][-1] in vowels or line[i][-1] == "m") and
					(line[i+1][0] in vowels or line[i+1][0] == "h")):
					if line[i+1] == "esse":
						line[i+1] = line[i+1][1:]
					else:
						line[i] = line[i][:-1]
		self.scansion = de_elided_text


	def mark_diphthongs(self):
		global vowels
		for i in xrange(len(self.scansion)):
			for j, word in enumerate(self.scansion[i]):
				word = word.replace("ae", "L")
				word = word.replace("au", "L")
				word = word.replace("eu", "L")
				word = word.replace("ei", "L")
				word = word.replace("oe", "L")
				self.scansion[i][j] = word


	def mark_naturally_long_vowels(self):
		latin_dict = Dictionary()
		for i in xrange(len(self.scansion)):
			for j in xrange(len(self.scansion[i])):
				indices = latin_dict.find_long_vowels(self.text.processed_text[i][j])
				for index in indices:
					if index == 0:
						self.scansion[i][j] = "L" + self.scansion[i][j][index + 1:]
					elif index == len(self.scansion[i][j]) - 1:
						self.scansion[i][j] = self.scansion[i][j][:index] + "L"
					elif index != -1:
						self.scansion[i][j] = self.scansion[i][j][:index] + "L" + self.scansion[i][j][index + 1:]


	def mark_lengthened_vowels(self):
		global vowels
		#exceptions = set(['c', 'k', 'g', 't', 'th', 'd', 'p', 'ph', 'b'])

		for line in self.scansion:
			for i in xrange(len(line)):
				for j in xrange(len(line[i]) - 2):
					if (line[i][j] in vowels and line[i][j + 1] in consonants and line[i][j + 2] in consonants):
						if j == 0:
							line[i] = 'L' + line[i][1:]
						else:
							line[i] = line[i][:j] + 'L' + line[i][j + 1:]
						j += 2


	def mark_last_foot(self):
		global vowels
		for line in self.scansion:
			for i in xrange(len(line[-1]) - 1, -1, -1):
				if line[-1][i] in vowels:
					if i == len(line[-1]) - 1:
						line[-1] = line[-1][:i] + 'L'
					elif i == 0:
						line[-1] = 'L' + line[-1][i+1:]
					else:
						line[-1] = line[-1][:i] + 'L' + line[-1][i+1:]
					break
				elif line[-1][i] == 'L':
					break


	def mark_remaining_as_short(self):
		global vowels
		for line in self.scansion:
			for i in xrange(len(line)):
				for j in xrange(len(line[i])):
					#if (line[i][j] in vowels and
					#	(j == 0 or (line[i][j-1] != 'S' and line[i][j-1] != 'L')) and
					#	(j == len(line[i]) - 1 or (line[i][j+1] != 'S' and line[i][j+1] != 'L'))):
					if line[i][j] in vowels:
						if j < len(line[i]) - 1 and j > 0:
							line[i] = line[i][:j] + 'S' + line[i][j + 1:]
						elif j > 0:
							line[i] = line[i][:j] + 'S'
						else:
							line[i] = 'S' + line[i][1:]


	def divide_verse_into_feet(self):
		self.divided_scansion = []
		count = 1
		for line in self.pure_scansion:
			curr_scansion = []
			for syllable in line:
				curr_scansion.append(syllable)
				if count == 2:
					if curr_scansion[-1] == 'L':
						curr_scansion.append('|')
						count = 1
				if count == 3:
					count = 1
					curr_scansion.append('|')
				count += 1
				curr_scansion.append(syllable)

			self.divided_scansion.append(curr_scansion)

			if self.divided_scansion[-1] == '|':
				self.divided_scansion = self.divided_scansion[:-1]


	def pure_scansion(self):
		pure_scansion = []
		for line in self.scansion:
			line_scansion = []
			for i, word in enumerate(line):
				for j in xrange(len(word)):
					if word[j] == 'S' or word[j] == 'L':
						line_scansion.append(word[j])
			pure_scansion.append(line_scansion)
		self.pure_scansion = pure_scansion


	def print_scansion_latex(self):
		pass



