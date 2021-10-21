## Add Root Dir
import sys
import os
ROOT_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(ROOT_DIR + "/source")

## Source
from namuParser import NamuWikiParser
from namuHeadExtractor import HeadExtractor
from namuTextExtractor import TextExtractor
from namuScorer import TableTextScorer
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
    if not os.path.exists(srcPath):
        print("Not Existed -", srcPath)
        return

    namuParser = NamuWikiParser(srcPath)
    print("INIT - Namuwiki Parser")
    print("PATH -", srcPath)

    docCnt = 0
    for document in namuParser.ParsingJSON():
        docCnt += 1

        if verbose and (0 == docCnt % printUnit):
            print(f'{docCnt}Processing... {document[DOC_TITLE]}')
            print(document[DOC_TEXT])
            print("--------------------------------------------\n")

        yield document

    print("END - Parsing,", srcPath)


def ParseParagraphFromFile(srcPath:str, verbose:bool=False, printUnit:int=1000):
    '''

    Args:
        srcPath: namuwiki json path (origin data)
        verbose: True - if you want to print processing count, set a 'True' otherwise 'False'
        printUnit: set a print verbose log cycle

    Returns:
        paragraph List by document
        Format - [ [paragraph index, table list, text list]... ]
    '''
    if not os.path.exists(srcPath):
        print("Not Existed -", srcPath)
        return

    namuParser = NamuWikiParser(srcPath)
    print("INIT - Namuwiki Parser")
    print("PATH -", srcPath)

    docCnt = 0
    for document in namuParser.ParsingJSON():
        docCnt += 1

        # Make paragraph list - [paragraph index, table list, text list]
        paragraphList = namuParser.ParseTableAndDetailsFromDocument(document[DOC_TITLE],
                                                                    document[DOC_TEXT])

        if verbose and 0 == (docCnt % printUnit):
            print(f'{docCnt}Processing... {document[DOC_TITLE]}')
            print(paragraphList)

        yield paragraphList


def ExtractMeaningTableAndSentences(srcPath:str, verbose:bool=False, printUnit:int=1000):
    '''

    Args:
        srcPath: namuwiki json path (origin data)
        verbose: True - if you want to print processing count, set a 'True' otherwise 'False'
        printUnit: set a print verbose log cycle

    Returns:
        [ ParagraphRelation ]
        list of paragraph in document
        Plz see a namuDef.py (ParagraphRelation)
    '''

    if not os.path.exists(srcPath):
        print("Not Existed -", srcPath)
        return

    # Object
    namuParser = NamuWikiParser(srcPath)
    headExtractor = HeadExtractor()
    textExtractor = TextExtractor()
    tableTextScorer = TableTextScorer()

    docCnt = 0
    for document in namuParser.ParsingJSON():
        docCnt += 1

        if verbose and (0 == docCnt % printUnit):
            print(f'{docCnt}Processing... {document[DOC_TITLE]}')

        paragraphList = namuParser.ParseTableAndDetailsFromDocument(document[DOC_TITLE],
                                                                    document[DOC_TEXT])
        paragraphRelationList = []
        for paragraph in paragraphList:
            paragraphRelation = ParagraphRelation()
            paragraphRelation.paragraphIdx = paragraph[0]
            paragraphRelation.tableRelation = list()

            ## Table
            if 0 < len(paragraph[1]):  # exist table
                newTableList = []
                modifiedTableList = namuParser.ModifyHTMLTags(paragraph[1])

                for table in modifiedTableList:
                    preprocessedTable = namuParser.PreprocessingTable(table)

                    if 2 <= len(preprocessedTable):
                        newTableList.append(preprocessedTable)

                # Not use infoBox, only use normal tables
                normalTableList, infoBoxList = namuParser.ClassifyNormalTableOrInfoBox(newTableList)
                existedHeadTableList = headExtractor.RemoveNoExistedTableHeaderTalbe(normalTableList)
                onlyTextTableList = textExtractor.ExtractTextAtTable(existedHeadTableList)
                meaningTableList = namuParser.RemoveDecoTables(onlyTextTableList)

                paragraph[1] = meaningTableList


            ## Sentences
            if 0 < len(paragraph[2]): # exist paragraph text
                textParagraphList = textExtractor.RemoveNamuwikiSyntax(paragraph[2])
                paragraph[2] = textParagraphList

            ## Add score between table and sequence
            if (0 < len(paragraph[1])) and (0 < len(paragraph[2])):
                # Make concat tables
                concatTableList = []
                for table in paragraph[1]:
                    mergeTable = []
                    for row in table:
                        mergeTable += row

                    concatStr = ' '.join(mergeTable)
                    concatTableList.append(concatStr)

                # Compute sentence core per concatTable
                tableSentenceDict = dict()  # key: int - table index, value: list - sentenceIndex

                for ctIdx, concatTable in enumerate(concatTableList):
                    scoreList = []

                    tableTextScorer.SetConcatTable(concatTable)

                    for sentence in paragraph[2]:
                        score = tableTextScorer.GetSentenceScore(sentence)
                        scoreList.append(score)

                    # Search highest score sentence
                    highScore = max(scoreList)
                    highSentenceIdx = scoreList.index(highScore)
                    tableSentenceDict[ctIdx] = highSentenceIdx

                # Make tableRelation and Add tableRelation to paragraphRelation
                for key, val in tableSentenceDict.items():
                    tableRelation = TableRelation()

                    table = paragraph[1][key]
                    tableRelation.table = table

                    tableRelation.sentences = paragraph[2][val]
                    paragraphRelation.tableRelation.append(tableRelation)

            else:
                # exist only table
                if 0 < len(paragraph[1]):  # table
                    for table in paragraph[1]:
                        tableRelation = TableRelation()
                        tableRelation.table = table
                        tableRelation.sentences = ''

                        paragraphRelation.tableRelation.append(tableRelation)

            paragraphRelationList.append(paragraphRelation)

            yield paragraphRelationList