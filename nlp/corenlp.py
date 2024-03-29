from stanfordcorenlp import StanfordCoreNLP
import logging
import json
import requests
import subprocess


class StanfordNLP:

    def __init__(self, host='http://localhost', port=9010):
        self.nlp = StanfordCoreNLP(host, port=port,
                                   timeout=30000)

        self.props = {
            'annotators': 'pos,parse,depparse,dcoref,relation',
            'pipelineLanguage': 'en',
            'outputFormat': 'json'
        }

    def pos(self, sentence):
        return self.nlp.pos_tag(sentence)

    def parse(self, sentence):
        return self.nlp.parse(sentence)

    def dependency_parse(self, sentence):
        return self.nlp.dependency_parse(sentence)

    def annotate(self, sentence):
        return json.loads(self.nlp.annotate(sentence, properties=self.props))

    @staticmethod
    def tokens_to_dict(_tokens):
        tokens = dict()
        for token in _tokens:
            tokens[int(token['index'])] = {
                'word': token['word'],
                'lemma': token['lemma'],
                'pos': token['pos'],
                'ner': token['ner']
            }
        return tokens


sNLP = StanfordNLP()

if __name__ == '__main__':
    text = 'Barack Obama was born in Hawaii.  He is the president. Obama was elected in 2008.'
    result = json.dumps(sNLP.annotate(text))
    print(result)
