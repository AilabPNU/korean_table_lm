import re
import sys

import numpy as np
from enum import Enum


## DefF
# Instance Type, link, image, digit, font, background color, and span
class INST_TYPE(Enum):
    NONE = 0
    LINK = 1
    IMAG = 2
    DIGIT = 3
    FONT = 4
    BG_COLOR = 5
    SPAN = 6


# Content pattern, Word(Str), Digit, Tag, specific charter
class CONTENT_PATT(Enum):
    NONE = 0
    WORD = 1
    DIGIT = 2
    TAG = 3
    SPEC_CHAR = 4


# Heurisitc Regex
HEURI_2_TBG = r'<tbg>{1}'
HEURI_2_BG = r'<bg>{1}'

HEURI_3_TEXT_ATTR = r'(<tf>)|(<tc>)'

HEURI_4_LINK = r'\[\[.+\]\]'
HEURI_4_IS_FLOAT = r'[\d]+\.[\d]+'
HEURI_4_IS_FONT = r'<tf>'
HEURI_4_IS_BG_COLOR = r'(<rbg>)|(<cbg>)'
HEURI_4_IS_SPAN = r'(<rs>)|(<cs>)'

HEURI_5_IS_FLOAT = HEURI_4_IS_FLOAT
HEURI_5_IS_TAG = HEURI_4_LINK

HEURI_6_ROW_SPAN = r'<rs>'
HEURI_6_COL_SPAN = r'<cs>'

HEURI_7_EMPTY = r'<[\w]+>|[\s]+'


class HeadExtractor:
    ### VAR ###

    ### INIT ###
    def __init__(self):
        print('INIT Extractor !!')

    ### PRIVATE ###
    '''
        @Heuristic
            Heuristic 5.1. If a <th> tag expresses a cell, then it has a high probability of being part of a HEAD.
        @Note
            Namuwiki data is not used '<th>', just use '||'
    '''

    def __Heuristic_1(self, srcTable):
        pass

    '''
        @Heuristic
            If a table is divided into two areas by background color, 
            the upper-side area or the left-side area has a high probability of being a HEAD.    
    '''

    def __Heuristic_2(self, srcTable):
        tableShape = (len(srcTable), len(srcTable[0]))
        retNpTable = np.zeros(tableShape, dtype=np.float64)

        # Check Divide with Background Color
        isTbg = False
        isBg = False
        for rIdx, row in enumerate(srcTable):
            for cIdx, col in enumerate(row):
                if re.search(HEURI_2_TBG, col):
                    isTbg = True
                if re.search(HEURI_2_BG, col):
                    isBg = True

        # Add Score
        if isTbg and isBg:
            for rIdx, row in enumerate(retNpTable):
                for cIdx, col in enumerate(row):
                    if (0 == rIdx) or (0 == cIdx):
                        retNpTable[rIdx, cIdx] = 1

        return retNpTable

    '''
        @Heuristic
            If a table is divided into two areas by font attributes,
            the upper-side area or the left-side area has a high probability of being a HEAD.

            When a table is in accordance with the third point in (3.2) in Section 3.1, DPH = “1,” 
            which is the highest value and the table consists of two areas. Intuitively, if a table has two areas, 
            with the two areas having a horizontal or a vertical distribution, 
            then the upper area or the left-hand area, respectively, have the higher probability of being a HEAD.
    '''

    def __Heuristic_3(self, srcTable):
        tableShape = (len(srcTable), len(srcTable[0]))
        retNpTable = np.zeros(tableShape, dtype=np.float64)

        textAttrList = []  # (rowIdx, colIdx)

        # Check Text Attribute row[0] or col[0]
        for rIdx, row in enumerate(srcTable):
            for cIdx, col in enumerate(row):
                if re.search(HEURI_3_TEXT_ATTR, col):
                    textAttrList.append((rIdx, cIdx))

        # Add Score - compare (0, cIdx), (rIdx, 0) with others attr count
        zeroIdxCnt = 0
        othersIdxCnt = 0
        for idxPair in textAttrList:
            if (0 == idxPair[0]) or (0 == idxPair[1]):
                zeroIdxCnt += 1
            else:
                othersIdxCnt += 1

        if zeroIdxCnt > othersIdxCnt:
            for idxPair in textAttrList:
                if (0 == idxPair[0]) or (0 == idxPair[1]):
                    retNpTable[idxPair[0], idxPair[1]] = 1

        return retNpTable

    '''
        @Heuristic
            If the cells in a row or a column are filled with a specific content instance type, 
            then a cell located in the extreme of the row or the column 
            (i.e., the left-hand or uppermost cell, respectively) has a high probability of being a part of the HEAD, 
            irrespective of its content instance type.
            In many meaningful tables, the content instance types
            (i.e., link, image, digit, font, background color, and span) are repetitive in some order in BODY.
    '''

    def __Heuristic_4(self, srcTable):
        tableShape = (len(srcTable), len(srcTable[0]))

        typeTable = [[set() for _ in range(tableShape[1])] for _ in range(tableShape[0])]
        ## Check Elements
        for rIdx, row in enumerate(srcTable):
            isRbg = False
            for cIdx, col in enumerate(row):
                onlyText = re.sub(r'<\w+>', '', col).replace(' ', '')

                # Check Link
                if re.search(HEURI_4_LINK, onlyText):
                    typeTable[rIdx][cIdx].add(INST_TYPE.LINK)

                ## Check Image - Not Used, Remove Tag in parsing step

                # Check Digit
                if not onlyText.isalnum() and (onlyText.isdigit() or re.search(HEURI_4_IS_FLOAT, onlyText)):
                    typeTable[rIdx][cIdx].add(INST_TYPE.DIGIT)

                # Check Font
                if re.search(HEURI_4_IS_FONT, col):
                    typeTable[rIdx][cIdx].add(INST_TYPE.FONT)

                # Check Background color
                if re.search(HEURI_4_IS_BG_COLOR, col):
                    # <rbg>
                    if re.search(r'<rbg>', col):
                        isRbg = True

                    # <cbg>
                    if re.search(r'<cbg>', col):
                        for rCbgIdx in range(tableShape[0]):
                            typeTable[rCbgIdx][0].add(INST_TYPE.BG_COLOR)

                # Check Span
                if re.search(HEURI_4_IS_SPAN, col):
                    typeTable[rIdx][cIdx].add(INST_TYPE.SPAN)

                if isRbg:
                    typeTable[rIdx][cIdx].add(INST_TYPE.BG_COLOR)

        ## Add Score
        retNpTable = self.__CheckInstanceType(typeTable, tableShape)
        return retNpTable

    '''
        Heuristic 4 Instance Type Checking
    '''

    def __CheckInstanceType(self, typeTable, tableShape):
        retNpTable = np.zeros(tableShape, dtype=np.float64)

        colInstSumDict = {
            INST_TYPE.LINK: [0 for _ in range(tableShape[1])],
            INST_TYPE.DIGIT: [0 for _ in range(tableShape[1])],
            INST_TYPE.FONT: [0 for _ in range(tableShape[1])],
            INST_TYPE.BG_COLOR: [0 for _ in range(tableShape[1])],
            INST_TYPE.SPAN: [0 for _ in range(tableShape[1])]
        }
        rowInstSumDict = {
            INST_TYPE.LINK: [0 for _ in range(tableShape[0])],
            INST_TYPE.DIGIT: [0 for _ in range(tableShape[0])],
            INST_TYPE.FONT: [0 for _ in range(tableShape[0])],
            INST_TYPE.BG_COLOR: [0 for _ in range(tableShape[0])],
            INST_TYPE.SPAN: [0 for _ in range(tableShape[0])]
        }

        for rIdx, row in enumerate(typeTable):
            for cIdx, col in enumerate(row):
                if INST_TYPE.LINK in col:
                    colInstSumDict[INST_TYPE.LINK][cIdx] += 1
                    rowInstSumDict[INST_TYPE.LINK][rIdx] += 1

                if INST_TYPE.DIGIT in col:
                    colInstSumDict[INST_TYPE.DIGIT][cIdx] += 1
                    rowInstSumDict[INST_TYPE.DIGIT][rIdx] += 1

                if INST_TYPE.FONT in col:
                    colInstSumDict[INST_TYPE.FONT][cIdx] += 1
                    rowInstSumDict[INST_TYPE.FONT][rIdx] += 1

                if INST_TYPE.BG_COLOR in col:
                    colInstSumDict[INST_TYPE.BG_COLOR][cIdx] += 1
                    rowInstSumDict[INST_TYPE.BG_COLOR][rIdx] += 1

                if INST_TYPE.SPAN in col:
                    colInstSumDict[INST_TYPE.SPAN][cIdx] += 1
                    rowInstSumDict[INST_TYPE.SPAN][rIdx] += 1

        # Add Score
        rowScoreCnt = tableShape[0] - 1
        colScoreCnt = tableShape[1] - 1

        for key, val in colInstSumDict.items():
            for vIdx, cnt in enumerate(val):
                if 0 == vIdx:
                    continue
                if cnt >= colScoreCnt:
                    retNpTable[0, vIdx] = 1

        for key, val in rowInstSumDict.items():
            for vIdx, cnt in enumerate(val):
                if 0 == vIdx:
                    continue
                if cnt >= rowScoreCnt:
                    retNpTable[vIdx, 0] = 1

        return retNpTable

    '''
        @Heuristic
            If the cells in a row or a column are filled with a specific content pattern, 
            then a cell located in the extreme of the row or the column
            (i.e., the most left-hand or uppermost, respectively) has a high probability of being a part of the HEAD, 
            irrespective of its content pattern.
            Cells have a particular sequence of token types.
            A token is a part of a sentence separated by specific delimiters such as space and punctuation marks,
            among others.
            We divide the into four type: word, digit, tag and specific charter.
    '''

    def __Heuristic_5(self, srcTable):
        tableShape = (len(srcTable), len(srcTable[0]))

        typeTable = [[set() for _ in range(tableShape[1])] for _ in range(tableShape[0])]

        ## Chcek Elements
        for rIdx, row in enumerate(srcTable):
            for cIdx, col in enumerate(row):
                isDigit = False
                isTag = False

                onlyText = re.sub(r"<\w+>", '', col).lstrip().rstrip()
                delSpace = onlyText.replace(' ', '')
                # Check Digit
                if not onlyText.isalnum() and (onlyText.isdigit() or re.search(HEURI_5_IS_FLOAT, delSpace)):
                    isDigit = True
                    typeTable[rIdx][cIdx].add(CONTENT_PATT.DIGIT)

                # Check tag
                if re.search(HEURI_5_IS_TAG, onlyText):
                    isTag = True
                    typeTable[rIdx][cIdx].add(CONTENT_PATT.TAG)

                if not isDigit and not isTag:
                    if onlyText.isalnum():
                        typeTable[rIdx][cIdx].add(CONTENT_PATT.WORD)

                # Check Specific charter - Not Used Namuwiki e.g) &lt, &frac...

        retNpTable = self.__CheckContentPattern(typeTable, tableShape)
        return retNpTable

    '''
        Check Content Pattern 
    '''

    def __CheckContentPattern(self, typeTable, tableShape):
        retNpTable = np.zeros(tableShape, dtype=np.float64)

        colPatternDict = {
            CONTENT_PATT.WORD: [0 for _ in range(tableShape[1])],
            CONTENT_PATT.DIGIT: [0 for _ in range(tableShape[1])],
            CONTENT_PATT.TAG: [0 for _ in range(tableShape[1])],
        }

        rowPatternDict = {
            CONTENT_PATT.WORD: [0 for _ in range(tableShape[0])],
            CONTENT_PATT.DIGIT: [0 for _ in range(tableShape[0])],
            CONTENT_PATT.TAG: [0 for _ in range(tableShape[0])]
        }

        # Word, Digit, Tag
        for rIdx, row in enumerate(typeTable):
            for cIdx, col in enumerate(row):
                if CONTENT_PATT.WORD in col:
                    colPatternDict[CONTENT_PATT.WORD][cIdx] += 1
                    rowPatternDict[CONTENT_PATT.WORD][rIdx] += 1

                if CONTENT_PATT.DIGIT in col:
                    colPatternDict[CONTENT_PATT.DIGIT][cIdx] += 1
                    rowPatternDict[CONTENT_PATT.DIGIT][rIdx] += 1

                if CONTENT_PATT.TAG in col:
                    colPatternDict[CONTENT_PATT.TAG][cIdx] += 1
                    rowPatternDict[CONTENT_PATT.TAG][rIdx] += 1

        # Add Score
        rowScoreCnt = tableShape[0] - 1
        colScoreCnt = tableShape[1] - 1

        for key, val in colPatternDict.items():
            for vIdx, cnt in enumerate(val):
                if 0 == vIdx:
                    continue
                if cnt >= colScoreCnt:
                    retNpTable[0, vIdx] = 1

        for key, val in rowPatternDict.items():
            for vIdx, cnt in enumerate(val):
                if 0 == vIdx:
                    continue
                if cnt >= rowScoreCnt:
                    retNpTable[vIdx, 0] = 1

        return retNpTable

    '''
        @Heuristic
            The rows and columns containing the “rowspan” or the “colspan” attributes of the <td> tag can be estimated 
            as being part of a HEAD when they are located in the extreme row or the column 
            (the left-hand or uppermost areas, respectively).
    '''

    def __Heuristic_6(self, srcTable):
        tableShape = (len(srcTable), len(srcTable[0]))
        retNpTable = np.zeros(tableShape, dtype=np.float64)

        colSpanList = []  # (row, idx), table[0][col]
        rowSpanList = []  # (row, idx), table[row][0]

        # Check Row/Col Span
        for rIdx, row in enumerate(srcTable):
            for cIdx, col in enumerate(row):
                if (0 == rIdx) and re.search(HEURI_6_COL_SPAN, col):
                    colSpanList.append((rIdx, cIdx))

                if (0 == cIdx) and re.search(HEURI_6_ROW_SPAN, col):
                    rowSpanList.append((rIdx, cIdx))

        # Add Score
        for spanPair in colSpanList:
            retNpTable[spanPair[0], spanPair[1]] = 1
        for spanPair in rowSpanList:
            retNpTable[spanPair[0], spanPair[1]] = 1

        return retNpTable

    '''
        @Heuristic
            If a table has an empty cell in the first row or first column, 
            the row and column that include that empty cell have a high probability of being the HEAD.
    '''

    def __Heuristic_7(self, srcTable):
        tableShape = (len(srcTable), len(srcTable[0]))
        retNpTable = np.zeros(tableShape, dtype=np.float64)

        # Check Empty table[0][0]
        cmpStr = re.sub(HEURI_7_EMPTY, '', srcTable[0][0])
        if 0 == len(cmpStr):
            # Add Score
            for ridx in range(tableShape[0]):
                retNpTable[ridx, 0] = 1
            for cIdx in range(tableShape[1]):
                retNpTable[0, cIdx] = 1

        return retNpTable

    '''
        @Note
            Compute (14), (15) equations of Section 5.3                         
    '''

    def __ComputeBinaryMatrices(self, scoreTableList, tableShape, weight):
        retTable = np.zeros(tableShape, dtype=np.float64)

        # Linear Interpolation
        linearInterpTable = np.zeros(tableShape, dtype=np.float64)
        for tIdx, table in enumerate(scoreTableList):
            linearInterpTable += (table * weight[tIdx])

        # MID
        # Get MAX(S_ij)
        maxVal = -1
        minVal = sys.maxsize
        for row in linearInterpTable:
            maxVal = max(maxVal, np.max(row))
            minVal = min(minVal, np.min(row))
        midVal = (maxVal + minVal) / 2

        # Make Result Matrix
        for rIdx, row in enumerate(linearInterpTable):
            for cIdx, col in enumerate(row):
                if midVal <= col:
                    retTable[rIdx, cIdx] = 1

        return retTable

    '''
        Check Existed Table Header
    '''

    def __CheckExistedTableHeader(self, scoreTable):
        retValue = False

        for row in scoreTable:
            for col in row:
                if 1.0 <= col:
                    retValue = True
                    break

            if retValue:
                break

        return retValue

    ### PUBLIC ###
    '''
        Extract Table Header
        @Note
            reference paper: A_scalable_hybrid_approach_for_extracting_head_components_from_Web_tables
            Please See a extracting heuristics of Section 6 in paper
        @Return
            Score Table List
    '''

    def GiveScoreToHeadCell(self, tableList):
        retTableList = []

        for table in tableList:
            # Use Heuristic
            # Not use Heuristic5_1, <th> was not included namu wiki data
            # resHeuri_1 = self.__Heuristic5_1(table)
            resHeuri_2 = self.__Heuristic_2(table)  # Check <tbg> and <bg>
            resHeuri_3 = self.__Heuristic_3(table)  # Check Text Attribute
            resHeuri_4 = self.__Heuristic_4(table)  # Check instance types
            resHeuri_5 = self.__Heuristic_5(table)  # Check content pattern
            resHeuri_6 = self.__Heuristic_6(table)  # Check Row and Col Span
            resHeuri_7 = self.__Heuristic_7(table)  # Check table[0][0] empty

            # Use Linear interpolation
            # Please See a Section 5.3 in paper
            tableShape = resHeuri_7.shape
            finalTable = self.__ComputeBinaryMatrices([resHeuri_2, resHeuri_3, resHeuri_4,
                                                       resHeuri_5, resHeuri_6, resHeuri_7], tableShape,
                                                      weight=[0.1, 0.2, 0.2, 0.1, 0.2, 0.2])

            # Append to return
            retTableList.append(finalTable)

        return retTableList

    '''
        if table head is not existed, remove the table
    '''

    def RemoveNoExistedTableHeaderTalbe(self, tableList):
        retTableList = []

        for table in tableList:
            resHeuri_2 = self.__Heuristic_2(table)  # Check <tbg> and <bg>
            resHeuri_3 = self.__Heuristic_3(table)  # Check Text Attribute
            resHeuri_4 = self.__Heuristic_4(table)  # Check instance types
            resHeuri_5 = self.__Heuristic_5(table)  # Check content pattern
            resHeuri_6 = self.__Heuristic_6(table)  # Check Row and Col Span
            resHeuri_7 = self.__Heuristic_7(table)  # Check table[0][0] empty

            tableShape = resHeuri_7.shape
            finalTable = self.__ComputeBinaryMatrices([resHeuri_2, resHeuri_3, resHeuri_4,
                                                       resHeuri_5, resHeuri_6, resHeuri_7], tableShape,
                                                      weight=[0.1, 0.2, 0.2, 0.1, 0.2, 0.2])

            isExistedHead = self.__CheckExistedTableHeader(finalTable)
            if isExistedHead:
                retTableList.append(table)

        return retTableList