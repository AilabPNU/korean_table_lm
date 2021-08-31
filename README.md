# korean_table_lm
한국어 테이블 언어모형

본 결과물의 코드 및 모델은 제32회 한글 및 한국어 정보처리 학술대회에서 발표했던 TAPAS를 이용한 사전학습 언어 모델 기반의 표 질의응답( http://hclt.kr/symp/?lnb=conference )을 기반으로 하고 있습니다.

![table_qa 이미지](https://user-images.githubusercontent.com/89840435/131489094-f54a4df1-2f3e-41d1-952a-e5a7a39d3db2.png)

본 모델은 KLUE의 RoBERTa를 가져와서 표 데이터에 사전학습하는 warm-start를 통해서 구축하였으며, 기존에 배포되었던 torch 모델 파일을 tensorflow에 맞게 변환하여 사용하였습니다. 

사전학습 데이터는 한국어 위키피디아에서 추출한 테이블 데이터를 활용했으며, 약 7만개의 일반 테이블과 약 10만 개의 인포박스 데이터를 활용하였습니다.

본 모델을 구축하기 위해 구현한 환경은 다음과 같습니다.
- tensorflow==1.13.1
- transformers (최신버전, tokenizer를 위해 사용)

roberta_table.py의 create_model에서 출력된 sequence_output 벡터를 적용할 태스크의 입력으로 사용하시면 됩니다. BERT 관련 코드는 BERT 깃헙의 tensorflow 코드를 활용하였습니다.


모델 다운로드: http://pnuailab.synology.me/sharing/8JtBA5IUn


출처 및 참고문헌


KLUE-roberta: https://huggingface.co/klue


BERT-github: https://github.com/google-research/bert
