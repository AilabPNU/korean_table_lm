from dataclasses import dataclass

DOC_TITLE = 'title'
DOC_TEXT = 'text'

@dataclass
class TableRelation:
    table = None
    sentences: str = ''

@dataclass
class ParagraphRelation:
    paragraphIdx: int = None
    tableRelation = list()

