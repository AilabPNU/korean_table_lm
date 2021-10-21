'''
    Define namu wiki syntax
'''

from enum import Enum

## Ref: https://namu.wiki/w/%EB%82%98%EB%AC%B4%EC%9C%84%ED%82%A4:%EB%AC%B8%EB%B2%95%20%EB%8F%84%EC%9B%80%EB%A7%90
class NAMU_RE(Enum):
    ## My Custom Attribute Token
    CUSTOM_ATTR = r'<\w+>'
    CUSTOM_BR = "{br}"

    ## Paragraph
    PARAGRAPH = r"={2,}#? .+ #?={2,}"

    # Is sentence end punctuation(.)?
    SENTENCE_PUNCT = r"\.$|\]$"

    ## Table
    ROW_SPLIT = r'\|\|'

    OLD_COL_SPAN = r'\|\|{2,}'
    NEW_COL_SPAN = r'<-\d+>'

    NEW_ROW_SPAN = r'<\|\d+>'

    ### Convert
    # 2.1
    TEXT_FORM = r"(''' '')|('' ''')|(''')|('')|__|~~|--" # Check Priority (''' '', ''')
    CONV_TEXT_FORM = "<tf>" # text form

    SUB_SCRIPT = r'\^\^|,,'
    CONV_SUB_SCRIPT = ' ' # white space

    # 2.3
    TEXT_COLOR = r'\{\{\{#\w+(,\s?#\w+)?\s?'
    CONV_TEXT_COLOR = '<tc>' # text color

    # 13.3.1
    BG_COLOR = r'<bgcolor=#?(\w|\d)+(,\s?#?\w+)?>'
    OLD_BG_COLOR = r'<#\w+>'
    CONV_BG_COLOR = '<bg>'

    TBG_COLOR = r'<(tablecolor|table\s?bgcolor)=#?\w+(,\s?#?\w+)?>'
    CONV_TBG_COLOR = '<tbg>'

    COL_BG_COLOR = r'<colbgcolor=#?\w+(,\s?#?\w+)?>'
    CONV_COL_BG_COLOR = '<cbg>'

    ROW_BG_COLOR = r'<rowbgcolor=#?\w+(,\s?#?\w+)?>'
    CONV_ROW_BG_COLOR = '<rbg>'

    CELL_COLOR = r'<color=#?\w+(,\s?#?\w+)?>'
    CONV_CELL_COLOR = '<celc>'

    COL_COLOR = r'<colcolor=#?\w+(,\s?#?\w+)?>'
    CONV_COL_COLOR = '<colc>'

    ROW_COLOR = r'<rowcolor=#?\w+(,\s?#?\w+)?>'
    CONV_ROW_COLOR = '<rowc>'

    ### Remove
    # 2.1
    LITERAL = r'\{\{\{\[\[|\]\]\}\}\}'

    # 2.2
    TEXT_SIZE_FRONT = r'\{\{\{(\+|-)\d\s*' # text size input's front

    # 3
    PARENT_ARTICLE_LINK = r'(\[\[)\.\./(\]\])'
    # CHILD_ARTICLIE_LINK = r'\[\[[/[\w]+]+'
    EXTERNAL_LINK = r'\[\[https?://[^\|(\]\])]\]\]'

    LINK_ALT_FRONT = r"\[\[[^\|\]]+\|"
    LINK_BASIC_FRONT = r"\[\["
    LINK_BACK = r"\]\]"

    # 5
    IMAGE_FILE = r'\[\[파일:[^\]]+(\|[^\]+])?\]\]'

    # 6
    YOUTUBE = r'\[youtube\(\w+(,\s?(start|width|height)=\w+%?)*\)\]|' \
                 r'\[include\(틀:.+ (left|center|right)?\s?url=\w+\)(,\s?(start|width|height)=\w+%?)*\]'
    KAKAO_TV = r'\[kakaotv\(\w+(,\s?(start|width|height)=\w+%?)*\)\]'
    NICO_VIDEO = r'\[nicovideo\(\w+(,\s?(start|width|height)=\w+%?)*\)\]'
    NAVER_VIDEO = r'\[include\(틀:(navertv|navervid){1}(,\s?(i=\w+|vid=\w+,\s?outkey=\w+)+)+(,\s?(start|width|height)=\w+%?)*\)\]'
    # 6 - deep syntax
    HTML_VIDEO = r'{{{#!html[^(}}})]+}}}'

    # 8
    ADD_LIST = r'v+(\w*\.|\*)?v*'
    BASIC_LIST = r"\*"

    # 9, 12.3
    FOOT_NOTE = r'\[\*.+\]|\[각주\]|\[footnote\]'

    # 10
    QUOTE = r">{1,}"

    # 11
    HORIZON_LINE = r"-{4,9}"

    # 12.1
    DOC_INSERT = r'\[include\(틀:[^\)]+\)\]'

    # 12.2
    AGE_FORM = r'\[age\(\d{4}-\d{1,2}-\d{1,2}\)\]'
    DATE_TIME_FORM = r'\[date\]|\[datetime\]'
    DDAY_FORM = r'\[dday\(\d{4}-\d{1,2}-\d{1,2}\)\]'

    # 12.3
    CONTENTS_TAG = r"\[목차\]|\[tableofcontents\]"

    # 12.4
    BR_TAG = r'(\[BR\])|(\[br\])'
    CLEARFIX = r'\[clearfix\]'

    # 13.3.1
    TABLE_ALIGN = r'<table\s?align=("|\')?(left|center|right)("|\')?>'
    TABLE_WIDTH = r'<table\s?width=\d+(px|%)?>'

    TABLE_BORDER_COLOR = r'<table\s?bordercolor=#?\w+(,#?\w+)?>'

    CELL_SIZE = r'<(width|height)=\d+(px|%)?>'

    CELL_H_ALIGN = r'(<\(>)|(<:>)|(<\)>)'
    CELL_V_ALIGN = r'(<\^\|\d+>)|(<v\|\d+>)'  # (<\|\d+>) ? -> row Span

    # 14
    FOLDING = r'\{\{\{#!folding\s?\[[^\[.]+\]'

    # macro - ruby
    MACRO_RUBY = r'\[ruby\(\w+, ruby=\w+\)\]'
    RUBY_FRONT = r'\[ruby\('
    RUBY_BACK = r',\s?ruby=.+\)\]'

    # tirple barket }}}
    TRIPLE_BARKET_BACK = r'}}}'