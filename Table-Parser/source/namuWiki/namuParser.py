## Built-in Module
import re
import sys
import os
import copy

## Pip Module
import pandas as pd
import ijson

## Definition File
from NamuWiki.NamuSyntax import NAMU_RE

## Definition
# Dict Def
DOC_TITLE = 'title'
DOC_TEXT = 'text'


class NamuWikiParser:
    ### VAR ###
    __srcPath = ''
    __normalTableCnt = 0
    __infoBoxCnt = 0

    ### INIT ###
    '''
        Initialize
        @Param
            jsonPath - wiki json path
    '''

    def __init__(self, jsonPath):
        self.__srcPath = jsonPath
        print('Init PreProcesser - JSON Path: ', self.__srcPath)

    ### PRIVATE ###
    def __ConvertTableColSpanToken(self, rowList):
        retRowList = []
        for row in rowList:
            if re.search(NAMU_RE.OLD_COL_SPAN.value, row):
                newRow = row
                colSpanList = re.findall(NAMU_RE.OLD_COL_SPAN.value, row)

                for colSpan in colSpanList:
                    spanCnt = len(re.findall(NAMU_RE.ROW_SPLIT.value, colSpan))
                    convStr = '||<-%s>' % spanCnt
                    newRow = row.replace(colSpan, convStr)

                retRowList.append(newRow)
            else:
                retRowList.append(row)

        return retRowList

    '''
        @Return
            retValue - True: Meaningfulness, False: Deco
    '''

    def __CheckRowIsEmptyCells(self, table):
        retValue = True

        for row in table:
            isEmpty = True
            for col in row:
                if 0 < len(str(col).lstrip()):
                    isEmpty = False
                    break

            if isEmpty:
                retValue = False
                break

        return retValue

    '''
        @Param
            ratio - ratio <= empty cell ratios, deco table
        @Return
            retValue - True: Meaningfulness, False: Deco
    '''

    def __CheckEmptyCellsRatio(self, table, ratio=0.3):
        retValue = True

        emptyCellCnt = 0
        totalCellCnt = 0
        for row in table:
            for col in row:
                totalCellCnt += 1

                stripCell = str(col).lstrip()
                if 0 >= len(stripCell):
                    emptyCellCnt += 1

        if ratio <= (emptyCellCnt / totalCellCnt):
            retValue = False

        return retValue

    ### PUBLIC ###
    '''
        Parse wiki json using ijson
    '''

    def ParsingJSON(self):
        with open(self.__srcPath, 'r', encoding='utf-8') as srcFile:
            parser = ijson.parse(srcFile)

            retValue = {}
            isNewKey = False
            for prefix, event, value in parser:
                if ('item', 'start_map') == (prefix, event):
                    isNewKey = True
                elif True == prefix.endswith('.title') and True == isNewKey:
                    retValue[DOC_TITLE] = value
                    retValue[DOC_TEXT] = []
                elif True == prefix.endswith('.text'):
                    retValue[DOC_TEXT].append(value)
                elif ('item', 'end_map') == (prefix, event):
                    yield retValue
                    isNewKey = False
                    retValue.clear()

    '''
        @Note
            Parse table and text which is related the table.

            Make [ [paragraphIdx, tableList, detailList] ]
            paragraphIdx: Integer
            tableList: [ table ]
            detailList: [ detail String ]
        @Param
            srcText - item.text, type(list)
                      len(docText) == 1
        @Return
            [ [paragraphIdx, tableList, detailList] ]
    '''

    def ParseTableAndDetailsFromDocument(self, srcTitle, srcText):
        retList = []

        if 0 >= len(srcText):
            print('ERROR - srcText length is 0', srcTitle)
            return

        docText = srcText[0]
        docSplitList = docText.split('\n')

        currParagraphIdx = 0

        tableList = []
        table = []

        detailList = []
        detailStr = ''
        for line in docSplitList:
            if re.search(NAMU_RE.PARAGRAPH.value, line):
                if 0 < len(table):
                    tableList.append(table)
                if 0 < len(detailStr):
                    detailList.append(detailStr)
                retList.append([currParagraphIdx, copy.deepcopy(tableList), copy.deepcopy(detailList)])
                currParagraphIdx += 1

                tableList.clear()
                table.clear()

                detailList.clear()
                detailStr = ''

            elif re.search(NAMU_RE.ROW_SPLIT.value, line):
                if 0 < len(detailStr):
                    detailList.append(detailStr)
                    detailStr = ''

                table.append(line)
            else:
                if 0 < len(table):
                    convertedTable = self.__ConvertTableColSpanToken(table)
                    tableList.append(convertedTable)
                    table.clear()

                detailStr += (NAMU_RE.CUSTOM_BR.value + line)

        # process last paragraph
        if 0 < len(table):
            convertedTable = self.__ConvertTableColSpanToken(table)
            tableList.append(convertedTable)
            table.clear()
        if 0 < len(detailStr):
            detailList.append(detailStr)
            detailStr = ''
        retList.append([currParagraphIdx, copy.deepcopy(tableList), copy.deepcopy(detailList)])

        return retList

    '''
        @Note
            All docText's len() is 1
        @Param
            docText - item.text, type(list)
    '''

    def ParseTableFromText(self, docText):
        retTableList = []

        re_checkRow = re.compile(NAMU_RE.ROW_SPLIT.value)
        for text in docText:
            splitList = text.split('\n')

            # Get Table
            tableRows = []
            for element in splitList:
                if re_checkRow.search(element):
                    tableRows.append(element)
                else:
                    if 0 < len(tableRows):
                        # Remove colspan r'[||]{2,}'
                        newRows = self.__ConvertTableColSpanToken(tableRows.copy())

                        retTableList.append(newRows)
                        tableRows.clear()

        return retTableList

    '''
        @Note
            Convert HTML Tags
            e.g.

            and Remove Others
    '''

    def ModifyHTMLTags(self, tableList):
        retTableList = []

        for table in tableList:
            newTable = []
            for idx, row in enumerate(table):
                newRow = row

                # Convert Tags
                newRow = re.sub(NAMU_RE.TEXT_FORM.value, NAMU_RE.CONV_TEXT_FORM.value, newRow)
                newRow = re.sub(NAMU_RE.SUB_SCRIPT.value, NAMU_RE.CONV_SUB_SCRIPT.value, newRow)
                newRow = re.sub(NAMU_RE.TEXT_COLOR.value, NAMU_RE.CONV_TEXT_COLOR.value, newRow)
                newRow = re.sub(NAMU_RE.BG_COLOR.value, NAMU_RE.CONV_BG_COLOR.value, newRow)
                newRow = re.sub(NAMU_RE.TBG_COLOR.value, NAMU_RE.CONV_TBG_COLOR.value, newRow)
                newRow = re.sub(NAMU_RE.COL_BG_COLOR.value, NAMU_RE.CONV_COL_BG_COLOR.value, newRow)
                newRow = re.sub(NAMU_RE.ROW_BG_COLOR.value, NAMU_RE.CONV_ROW_BG_COLOR.value, newRow)
                newRow = re.sub(NAMU_RE.CELL_COLOR.value, NAMU_RE.CONV_CELL_COLOR.value, newRow)
                newRow = re.sub(NAMU_RE.COL_COLOR.value, NAMU_RE.CONV_COL_COLOR.value, newRow)
                newRow = re.sub(NAMU_RE.ROW_COLOR.value, NAMU_RE.CONV_ROW_COLOR.value, newRow)

                # Remove Tags
                newRow = re.sub(NAMU_RE.LITERAL.value, '', newRow)
                newRow = re.sub(NAMU_RE.TEXT_SIZE_FRONT.value, '', newRow)
                newRow = re.sub(NAMU_RE.PARENT_ARTICLE_LINK.value, '', newRow)
                newRow = re.sub(NAMU_RE.IMAGE_FILE.value, '', newRow)  # Check Order
                newRow = re.sub(NAMU_RE.EXTERNAL_LINK.value, '', newRow)  # Check Order
                newRow = re.sub(NAMU_RE.YOUTUBE.value, '', newRow)
                newRow = re.sub(NAMU_RE.KAKAO_TV.value, '', newRow)
                newRow = re.sub(NAMU_RE.NICO_VIDEO.value, '', newRow)
                newRow = re.sub(NAMU_RE.NAVER_VIDEO.value, '', newRow)
                newRow = re.sub(NAMU_RE.HTML_VIDEO.value, '', newRow)
                newRow = re.sub(NAMU_RE.ADD_LIST.value, '', newRow)
                newRow = re.sub(NAMU_RE.FOOT_NOTE.value, '', newRow)
                newRow = re.sub(NAMU_RE.AGE_FORM.value, '', newRow)
                newRow = re.sub(NAMU_RE.DATE_TIME_FORM.value, '', newRow)
                newRow = re.sub(NAMU_RE.DDAY_FORM.value, '', newRow)
                newRow = re.sub(NAMU_RE.BR_TAG.value, '', newRow)
                newRow = re.sub(NAMU_RE.TABLE_ALIGN.value, '', newRow)
                newRow = re.sub(NAMU_RE.TABLE_WIDTH.value, '', newRow)
                newRow = re.sub(NAMU_RE.TABLE_BORDER_COLOR.value, '', newRow)
                newRow = re.sub(NAMU_RE.CELL_SIZE.value, '', newRow)
                newRow = re.sub(NAMU_RE.CELL_H_ALIGN.value, '', newRow)
                newRow = re.sub(NAMU_RE.CELL_V_ALIGN.value, '', newRow)
                newRow = re.sub(NAMU_RE.FOLDING.value, '', newRow)
                newRow = re.sub(NAMU_RE.TRIPLE_BARKET_BACK.value, '', newRow)

                # Exception
                newRow = re.sub(NAMU_RE.OLD_BG_COLOR.value, NAMU_RE.CONV_BG_COLOR.value, newRow)
                # newRow = re.sub(NAMU_RE.LINK_BACK.value, '', newRow)

                # Ruby
                if re.search(NAMU_RE.MACRO_RUBY.value, newRow):
                    rubyList = re.findall(NAMU_RE.MACRO_RUBY.value, newRow)

                    for rubyStr in rubyList:
                        delRubyStr = re.sub(NAMU_RE.RUBY_FRONT.value, '', rubyStr)
                        delRubyStr = re.sub(NAMU_RE.RUBY_BACK.value, '', delRubyStr)
                        newRow = newRow.replace(rubyStr, delRubyStr)
                newTable.append(newRow)
            retTableList.append(newTable)

        return retTableList

    '''
        Split Row and Col by '||'
    '''

    def SplitRowAndColByToken(self, table):
        retTable = []

        for row in table:
            newRow = []
            spliteRowList = re.split(NAMU_RE.ROW_SPLIT.value, row)[1:-1]

            for col in spliteRowList:
                newRow.append(col)
            retTable.append(newRow)

        return retTable

    '''
        Split Col Span
    '''

    def SplitColSpan(self, table):
        retTable = []

        for row in table:
            newRow = []

            for col in row:
                if re.search(NAMU_RE.NEW_COL_SPAN.value, col):
                    spanCnt = int(
                        re.search(NAMU_RE.NEW_COL_SPAN.value, col).group(0).replace('<-', '').replace('>', ''))
                    newCol = re.sub(NAMU_RE.NEW_COL_SPAN.value, '<cs>', col)
                    for spIdx in range(spanCnt):
                        newRow.append(newCol)
                else:
                    newRow.append(col)
            retTable.append(newRow)

        return retTable

    '''
        Split Row Span
    '''

    def SplitRowSpan(self, table):
        retTable = []

        spanInfoList = []  # (colIdx, str, spanCnt)
        for row in table:
            newRow = []

            for cIdx, col in enumerate(row):
                if re.search(NAMU_RE.NEW_ROW_SPAN.value, col):
                    spanCnt = int(
                        re.search(NAMU_RE.NEW_ROW_SPAN.value, col).group(0).replace("<|", '').replace(">", ''))
                    newCol = re.sub(NAMU_RE.NEW_ROW_SPAN.value, '<rs>', col)
                    spanInfo = (cIdx, newCol, spanCnt - 1)
                    spanInfoList.append(spanInfo)

                    newRow.append(newCol)
                else:
                    for infoIdx, infoData in enumerate(spanInfoList):
                        if cIdx == infoData[0]:
                            newRow.append(infoData[1])
                            if 0 >= infoData[2] - 1:
                                spanInfoList.remove(infoData)
                            else:
                                newInfo = (infoData[0], infoData[1], infoData[2] - 1)
                                spanInfoList[infoIdx] = newInfo
                    newRow.append(col)
            retTable.append(newRow)

        return retTable

    '''
        Remove Empty Cells
    '''

    def RemoveEmptyRows(self, table):
        retTable = []

        for row in table:
            if 0 < len(row):
                retTable.append(row)

        return retTable

    '''
        Slice Table Length with min length
    '''

    def SliceTableLength(self, table):
        retTable = []

        # Check Table Min Length
        minLen = sys.maxsize
        for row in table:
            minLen = min(minLen, len(row))

        # Slice row of table
        for row in table:
            newRow = row[:minLen]
            retTable.append(newRow)

        return retTable

    '''
        Classify Normal Table and Info Box
        @Param
            Origin Table List (Source Table)
        @Return
            normalTableList, infoBoxList
    '''

    def ClassifyNormalTableOrInfoBox(self, tableList):
        normalTableList = []
        infoBoxList = []

        for table in tableList:
            colLen = len(table[0])
            if 3 <= colLen:
                normalTableList.append(table)
            else:
                infoBoxList.append(table)

        return normalTableList, infoBoxList

    '''
        Merge Related Process 
    '''

    def PreprocessingTable(self, table):
        retTable = table

        ## Preprocess
        retTable = self.SplitRowAndColByToken(table)
        retTable = self.SplitColSpan(retTable)
        retTable = self.SplitRowSpan(retTable)
        retTable = self.RemoveEmptyRows(retTable)
        retTable = self.SliceTableLength(retTable)

        return retTable

    '''
        Write Tables
    '''

    def WriteTableToFile(self, tableList, title, destPath, isNormalTable):
        if not os.path.exists(destPath):
            print('Check Path: ', destPath)
            return

        fileIdx = 0
        if isNormalTable:
            fileIdx = self.__normalTableCnt
            self.__normalTableCnt += 1
        else:
            fileIdx = self.__infoBoxCnt
            self.__infoBoxCnt += 1

        for tIdx, table in enumerate(tableList):
            fileName = 'table_' + str(tIdx) + '.tsv'

            tablePd = pd.DataFrame(table)
            tablePd.to_csv(destPath + '/' + str(fileIdx) + '_' + fileName, sep='\t', encoding='utf-8')

    '''
        Extract Only Text in column data
    '''

    def ExtractTextDataInColumn(self, tableList):
        retTableList = []

        for table in tableList:
            newTable = []

            for row in table:
                newRow = []

                for col in row:
                    newCol = re.sub(r"<\w+>", '', col)
                    newCol = re.sub(r"\[\[.+\|", '', newCol)
                    newCol = re.sub(r'\]\]', '', newCol)

                    newRow.append(newCol)
                newTable.append(newRow)
            retTableList.append(newTable)

        return retTableList

    '''
        Remove Deco Table
    '''

    def RemoveDecoTables(self, tableList):
        retTableList = []

        for table in tableList:
            # Check Method 1
            isMT = self.__CheckRowIsEmptyCells(table)
            if not isMT:
                continue

            # Check Method 2
            isMT = self.__CheckEmptyCellsRatio(table, ratio=0.3)

            if isMT:
                retTableList.append(table)

        return retTableList