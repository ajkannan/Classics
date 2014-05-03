import re
from os import listdir

def convert_xml_to_text(filename):
	xml_input = open(filename, 'r')
	parsed_text = ""
	found_start = False
	for xml_line in xml_input.readlines():
		if found_start:
			parsed_text += re.sub("<.*?>", "", xml_line).strip()
			parsed_text += "\n"
		elif '<text>' in xml_line or '<text ' in xml_line:
			found_start = True

	xml_input.close()
	text_output = open(filename[:-4] + ".txt", 'w')
	text_output.write(parsed_text)
	text_output.close()

if __name__ == "__main__":
	files = listdir("./Texts")
	for file in files:
		convert_xml_to_text("./Texts/" + file)
