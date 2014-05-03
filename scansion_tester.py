from Utilities.Text import Text
from Utilities.Scansion import Scansion

from pprint import pprint

if __name__ == "__main__":
	jfk = Text("Texts/Seneca/agammemnon.txt")
	print jfk.concatenated_text
	tester = Scansion(jfk)
	print tester.scansion
	print tester.divided_scansion
