## Add Root Dir
import sys
import os
ROOT_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(ROOT_DIR + "/source")

## Source
from namuParser import NamuWikiParser
from namuDef import *

def ParseNuamuJsonDoc(srcPath:str, verbose:bool=False, printUnit:int=1000):
    '''
    Args:
        srcPath: namuwiki json path (origin data)
        verbose: True - if you want to print processing count, set a 'True' otherwise 'False'
        printUnit: set a print verbose log cycle

    Returns:
        Return per document
        Type - dict()
        E.g. {'title': '!', 'text': ['#redirect 느낌표\n']}
    '''
    namuParser = NamuWikiParser(srcPath)
    print("INIT - Namuwiki Parser")
    print("PATH -", srcPath)

    docCnt = 0
    for document in namuParser.ParsingJSON():
        docCnt += 1

        if verbose and (0 == docCnt % printUnit):
            print(f"{docCnt} Processing... {document[DOC_TITLE]}")
            print(document[DOC_TEXT])
            print("--------------------------------------------\n")

        yield document

    print("END - Parsing,", srcPath)