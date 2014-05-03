import sys
from pprint import pprint, pformat
import numpy as np

def parse_txt_file(filename):
	text_input = open(filename, 'r')
	first_line = True
	results_dict = {}
	first_line = True
	last_line = False
	current_line = ""
	bhattacharyya_data = {}

	while ")])]}" not in current_line:
		current_line = text_input.readline().strip()
		if first_line:
			current_line = current_line.replace("{", "")
			first_line = False

		# Starting an new passage length
		first_word = current_line.split(" ")[0]
		passage_length = int(first_word[:-1])
		bhattacharyya_data[passage_length] = []
		results_dict[passage_length] = []
		beginning_of_block = True

		# Read all the intertext for a specific passage length
		while ")])]" not in current_line:
			if beginning_of_block:
				beginning_of_block = False
			else:
				current_line = text_input.readline()

			# Read the query passage belonging to document 1
			current_result = []
			start_query_passage = current_line.index("('") + 2
			end_query_passage = current_line.index("',")
			query_passage = current_line[start_query_passage:end_query_passage]
			current_result.append(query_passage)

			# Read in the intertextuality proportion
			proportion = float(text_input.readline().strip()[:-1])
			current_result.append(proportion)

			# Read in the list of passages belonging to document 2
			document_two_passages = []
			while ")])" not in current_line:
				passage = text_input.readline().strip()
				passage = passage[passage.index("('") + 2:passage.index("',")]
				bhattacharyya_distance = float(text_input.readline().strip()[:-1])
				bhattacharyya_data[passage_length].append(bhattacharyya_distance)

				current_line = text_input.readline().strip()
				passage_index = int(current_line[:current_line.index(")")])
				document_two_passages.append((passage, bhattacharyya_distance, passage_index))
			current_result.append(document_two_passages)
			results_dict[passage_length].append(tuple(current_result))

	text_input.close()

	results_file = open('results_dictionary.txt', 'w')
	results_file.write(pformat(results_dict))
	results_file.close()

	bhat_csv_file = open('bhattacharyya_distance_csv.txt', 'w')
	for passage_length in bhattacharyya_data.keys():
		bhat_csv_file.write(str(passage_length) + ", ")
		for i, distance in enumerate(bhattacharyya_data[passage_length]):
			bhat_csv_file.write(str(distance))
			if i < len(bhattacharyya_data[passage_length]) - 1:
				bhat_csv_file.write(", ")
		bhat_csv_file.write("\n")
	bhat_csv_file.close()


if __name__ == "__main__":
	parse_txt_file(sys.argv[1])
