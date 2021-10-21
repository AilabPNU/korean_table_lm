import sys
import os
ROOT_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(ROOT_DIR + "/api")

# api
from api_namu import *

# Example
if __name__ == "__main__":
     srcPath = "../dataset/wikiDocData200302.json"
     for retDoc in ParseParagraphFromFile(
             srcPath=srcPath,
             verbose=False):
          print(retDoc)