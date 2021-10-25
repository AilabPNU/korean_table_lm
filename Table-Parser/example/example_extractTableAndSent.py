import sys
import os
ROOT_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(ROOT_DIR + "/api")

# api
from api_namu import *


if __name__ == "__main__":
    srcPath = "../dataset/wikiDocData200302.json"

    for retVal in ExtractMeaningTableAndSentences(
            srcPath=srcPath,
            verbose=False):

        for paragraphRel in retVal:
            print(paragraphRel.paragraphIdx)

            for tableRel in paragraphRel.tableRelation:
                print(tableRel.table)
                print(tableRel.sentences)