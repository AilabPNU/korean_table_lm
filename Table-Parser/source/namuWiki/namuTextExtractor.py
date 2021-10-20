'''
    @Note
        Extract text only
        Remove text attr, size, color, background color, hyper-link....
'''
import re
from namuSyntax import NAMU_RE

class TextExtractor:
    ### VAR ###


    ### PRIVATE ###


    ### PUBLIC ####
    def __init__(self):
        print('INIT TextExtractor !')

    '''
        @Note
            Extract Text and remove <\w+> from table
        @Param
            tableList (source)
        @Return
            retTableList (include only text)
    '''
    def ExtractTextAtTable(self, tableList):
        retTableList = []

        for table in tableList:
            newTable = []
            for row in table:
                newRow = []
                for col in row:
                    newCol = re.sub(r"<\w+>", '', col) # attr tag
                    #newCol = re.sub(NAMU_RE.LINK_ALT_FRONT.value, '', newCol) # [[.+|.+]]
                    #newCol = re.sub(NAMU_RE.LINK_BASIC_FRONT.value, '', newCol) # [[.+]]
                    #newCol = re.sub(NAMU_RE.LINK_BACK.value, '', newCol) # [[.+|.+]] and [[.+]]

                    newRow.append(newCol)
                newTable.append(newRow)
            retTableList.append(newTable)

        return retTableList

    '''
        @Note
            Remove Namu-wiki syntax
        @Param
            srcString (length is 1)
        @Return
            retStringList (split by '.')
    '''
    def RemoveNamuwikiSyntax(self, srcList):
        retStrList = []

        for srcStr in srcList:
            splitStrList = srcStr.split(NAMU_RE.CUSTOM_BR.value + NAMU_RE.CUSTOM_BR.value) # \n\n
            for splitStr in splitStrList:
                # Delete \n
                splitStr = re.sub(NAMU_RE.CUSTOM_BR.value, '', splitStr)
                splitStr = splitStr.lstrip().rstrip()

                # Check '.' punctuation
                if not re.search(NAMU_RE.SENTENCE_PUNCT.value, splitStr):
                    continue

                # re
                newStr = re.sub(NAMU_RE.IMAGE_FILE.value, '', splitStr)
                newStr = re.sub(NAMU_RE.YOUTUBE.value, '', newStr)
                newStr = re.sub(NAMU_RE.KAKAO_TV.value, '', newStr)
                newStr = re.sub(NAMU_RE.NICO_VIDEO.value, '', newStr)
                newStr = re.sub(NAMU_RE.NAVER_VIDEO.value, '', newStr)
                newStr = re.sub(NAMU_RE.HTML_VIDEO.value, '', newStr)
                newStr = re.sub(NAMU_RE.EXTERNAL_LINK.value, '', newStr)
                newStr = re.sub(NAMU_RE.DOC_INSERT.value, '', newStr)

                newStr = re.sub(NAMU_RE.TEXT_FORM.value, '', newStr)
                newStr = re.sub(NAMU_RE.SUB_SCRIPT.value, '', newStr)
                newStr = re.sub(NAMU_RE.TEXT_SIZE_FRONT.value, '', newStr)
                newStr = re.sub(NAMU_RE.TEXT_COLOR.value, '', newStr)
                newStr = re.sub(NAMU_RE.LITERAL.value, '', newStr)
                newStr = re.sub(NAMU_RE.LINK_ALT_FRONT.value, '', newStr)
                newStr = re.sub(NAMU_RE.LINK_BASIC_FRONT.value, '', newStr)
                newStr = re.sub(NAMU_RE.ADD_LIST.value, '', newStr)
                newStr = re.sub(NAMU_RE.BASIC_LIST.value, '', newStr)
                newStr = re.sub(NAMU_RE.FOOT_NOTE.value, '', newStr)
                newStr = re.sub(NAMU_RE.QUOTE.value, '', newStr)
                newStr = re.sub(NAMU_RE.HORIZON_LINE.value, '', newStr)
                newStr = re.sub(NAMU_RE.AGE_FORM.value, '', newStr)
                newStr = re.sub(NAMU_RE.DATE_TIME_FORM.value, '', newStr)
                newStr = re.sub(NAMU_RE.DDAY_FORM.value, '', newStr)
                newStr = re.sub(NAMU_RE.CONTENTS_TAG.value, '', newStr)
                newStr = re.sub(NAMU_RE.BR_TAG.value, '', newStr)
                newStr = re.sub(NAMU_RE.CLEARFIX.value, '', newStr)
                newStr = re.sub(NAMU_RE.FOLDING.value, '', newStr)

                newStr = re.sub(NAMU_RE.LINK_BACK.value, '', newStr)
                newStr = re.sub(NAMU_RE.TRIPLE_BARKET_BACK.value, '', newStr)

                # 12. Macro - Ruby
                if re.search(NAMU_RE.MACRO_RUBY.value, newStr):
                    rubyList = re.findall(NAMU_RE.MACRO_RUBY.value, newStr)

                    for rubyStr in rubyList:
                        delRubyStr = re.sub(NAMU_RE.RUBY_FRONT.value, '', rubyStr)
                        delRubyStr = re.sub(NAMU_RE.RUBY_BACK.value, '', delRubyStr)
                        newStr = newStr.replace(rubyStr, delRubyStr)

                # Exception (Last Process)
                newStr = re.sub(r'\[[^\]]+\]', '', newStr)

                # Add newStr to return list
                if 0 < len(newStr.lstrip()):
                    retStrList.append(newStr.lstrip())

        return retStrList