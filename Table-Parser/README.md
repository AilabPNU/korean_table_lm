# Table Parser 
- 나무위키에서 정보를 담고있는 테이블을 2D List로 얻기 위한 API

## 폴더 구조
 ```
    ├─Table-Parser
    │  ├─api
    │  │  ├─api_namu.py
    │  ├─example
    │  │  ├─example_extractTableAndSent.py
    │  │  ├─example_parseJson.py
    │  │  ├─example_parseParagraph.py
    │  ├─source
    │  │  ├─namuDef.py
    │  │  ├─namuHeadExtractor.py
    │  │  ├─namuParser.py
    │  │  ├─namuScorer.py
    │  │  ├─namuSyntax.py
    │  │  ├─namuTextExtractor.py
```

##  NAMU API 소개
- callable method는 아래 3개이다.
 1. ParseNuamuJsonDoc(srcPath:str, verbose:bool=False, printUnit:int=1000)
    - 나무위키 문법이 포함된 Json Document 파일에서 Python Dictionary 로 각 문서별 Return 한다.
    - Return: {'titile' str, 'text': list}
 2. ParseParagraphFromFile(srcPath:str, verbose:bool=False, printUnit:int=1000)
    - 나무위키 문법이 포함된 Json Document 파일에서 각 문서의 문단별로 REturn 한다.
    - Return: Type List, [ [paragraph index, table list, text list] ]
 3. ExtractMeaningTableAndSentences(srcPath:str, verbose:bool=False, printUnit:int=1000)
    - 나무위키 문법이 포함된 Json Document 파일에서 각 문서별 의미있는 테이블과 그에 관련된 Sentences를 Return한다.
    - Return: Cusom Data Structure, [ ParagraphRelation ] (namuDef.py를 참조)
<br>

- 3개의 Method 모두 필요한 Parameter는 동일하다.
  - srcPath: 나무위키 JSON 파일
  - verbose: printUnit 단위마다 Log 출력여부
  - printUnit: verbose가 True일 경우 몇 번의 document마다 Log를 출력을 할 것인지 설정. 

## 참고 문헌
Table Head 추출을 위한 Heuristic - [A Scalable Hybrid Approach For Extracting Head Components From Web Tables](https://ieeexplore.ieee.org/document/1563981)
