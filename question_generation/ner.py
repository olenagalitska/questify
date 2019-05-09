from nltk.tag import StanfordNERTagger

NER_4_CLASSIFIER = '/Users/olenagalitska/Developer/questify/question_generation/english.conll.4class.distsim.crf.ser.gz'
NER_7_CLASSIFIER = '/Users/olenagalitska/Developer/questify/question_generation/english.muc.7class.distsim.crf.ser.gz'
NER_JAR_PATH = '/Users/olenagalitska/Developer/questify/question_generation/stanford-ner.jar'


def get_ner_tags(phrase):
    ner4_result = StanfordNERTagger(NER_4_CLASSIFIER, NER_JAR_PATH).tag(phrase.split())
    ner7_result = StanfordNERTagger(NER_7_CLASSIFIER, NER_JAR_PATH).tag(phrase.split())
    final_result = set(
        list(filter(lambda x: x[1] != "O", ner4_result)) + list(filter(lambda x: x[1] != "O", ner7_result)))
    return list(final_result)


def get_ner_tag(word):
    tags = get_ner_tags(word)
    if len(tags) > 0:
        tag = tags[0]
        if tag[1] != 'O':
            return tag


if __name__ == "__main__":
    print(get_ner_tags("Mike was born on August 4, 1961 in Honolulu, Hawaii which was 4 days ago."))
