from eunjeon import Mecab

class TableTextScorer:
    ### VAR ###


    ### PRIVATE ###


    ### PUBLIC ###
    def __init__(self):
        self.tagger = Mecab()
        self.Bi_character_feature = []
        print('INIT TableDetailScorer')

    '''
        Set table element string using by concat(.joint())
    '''
    def SetConcatTable(self, table):
        self.Bi_character_feature = []
        TKs = self.tagger.morphs(table)

        for TK in TKs:
            if 1 < len(TK):
                for idx in range(1, len(TK)):
                    self.Bi_character_feature.append(str(TK[idx-1:idx+1]))

    '''
        Compute Score     
    '''
    def GetSentenceScore(self, sentence):
        score = 0

        for ch_feat in self.Bi_character_feature:
            if sentence.find(ch_feat) != -1:
                score += 1
        if 0 == len(self.Bi_character_feature):
            return 1

        return 1 + (score / len(self.Bi_character_feature))