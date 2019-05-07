import nltk
import spacy
import requests
from question_generation import ner, corenlp

RULES_PATH = '/Users/olenagalitska/Developer/questify/question_generation/wh_rules.txt'


def get_rule_patterns():
    file = open(RULES_PATH, 'r')
    p = file.readlines()
    file.close()
    return p


def get_text_from_node(node, sentence):
    node_phrase = node.replace(')', ' ')
    res = [l for l in node_phrase.split() if l in sentence.split()]
    return " ".join(res)


patterns = get_rule_patterns()


def get_tregex_matches(pattern, sentence, key_name):
    result = list()
    url = "http://localhost:9010/tregex"
    r = requests.post(url, data=sentence.encode('utf-8'), params={"pattern": pattern})
    if r.ok:
        for s in r.json()['sentences']:
            for key, value in s.items():
                result.append(value[key_name])
    return result


def get_question(sentence):
    # print(corenlp.sNLP.parse(sentence))

    sentence = sentence.replace(".", "")
    questions = set()
    unmovable_phrases = set()
    url = "http://localhost:9010/tregex"

    answer_nodes = get_tregex_matches('NP', sentence, 'match') + \
                   get_tregex_matches('PP', sentence, 'match') + \
                   get_tregex_matches('SBAR', sentence, 'match')

    for pattern in patterns:
        request_params = {"pattern": pattern}
        r = requests.post(url, data=sentence.encode('utf-8'), params=request_params)
        if r.ok and '0' in r.json()['sentences'][0]:
            unmovable_nodes = r.json()['sentences'][0]['0']['namedNodes']
            for node in unmovable_nodes:
                if node['unmv'] in answer_nodes:
                    answer_nodes.remove(node['unmv'])
    verb_selector = get_tregex_matches(
        "ROOT < (S=clause < (VP=mainvp [ < (/VB.?/=tensed !< is|was|were|am|are|has|have|had|do|does|did)| < /VB.?/=tensed !< VP ]))",
        sentence, 'namedNodes')
    for names in verb_selector:
        mainvp = ""
        for name in names:
            if 'mainvp' in name:
                mainvp = name['mainvp']

        main_verb = get_text_from_node(mainvp, sentence)

        # main_verb = get_text_from_node(get_tregex_matches('VP', sentence, 'match')[0], sentence)

        # main_clause_pattern = "ROOT=root < (S=clause <+(/VP.*/) (VP < (/VB.?/=copula < is|are|was|were|am) !< VP))"
        # main_clause_selector = get_tregex_matches(main_clause_pattern, sentence, "namedNodes")
        # print(main_clause_selector)
        if main_verb != '':
            questions.add(main_verb)
            questions.add('What ' + main_verb + '?')
    for answer_node in answer_nodes:
        text = get_text_from_node(answer_node, sentence)
        # print(text)
        # questions.add(sentence.replace(' ' + text + ' ', ' __________________ '))
    for question in questions:
        # print(sentence)
        print(question)
    return questions


def generate_questions(sentences):
    questions = set()
    for sentence in sentences:
        sentence_questions = get_question(sentence)
        for q in sentence_questions:
            questions.add(q)
    return questions


if __name__ == "__main__":
    # from text_processing import text_prep

    # s = text_prep.get_ranked_sentences_lexrank("../text_processing/text_files/raw_input.txt")
    # generate_questions(s)
    get_question("James arrived before the bus left.")
