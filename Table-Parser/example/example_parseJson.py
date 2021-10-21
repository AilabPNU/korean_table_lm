import sys
import os
ROOT_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(ROOT_DIR + "/api")

# api
from api_namu import *

# Example
if __name__ == "__main__":
     for retDoc in ParseNuamuJsonDoc(
             srcPath="C:/Users/JaeHoon/Desktop/Git/korean_table_lm/Table-Parser/dataset/wikiDocData200302.json",
             verbose=False):
         print(retDoc)