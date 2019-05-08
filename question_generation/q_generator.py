import nltk
import spacy
import requests
from question_generation import ner, corenlp, simplify_sentence
from nltk.stem.wordnet import WordNetLemmatizer

WH_RULES_PATH = '/Users/olenagalitska/Developer/questify/question_generation/wh_rules.txt'
ANSWER_POS_RULES = '/Users/olenagalitska/Developer/questify/question_generation/answer_pos.txt'


def get_rule_patterns(path):
    file = open(path, 'r')
    p = file.readlines()
    file.close()
    return p


def get_lemma(word, type):
    return WordNetLemmatizer().lemmatize(word, type)


def get_text_from_node(node, sentence):
    node_phrase = node.replace(')', ' ')
    # print(node_phrase)
    s = list()
    for word in sentence.split():
        if ',' in word:
            s.append(word.replace(',', ''))
            s.append(',')
        if '.' in word:
            s.append(word.replace('.', ''))
            s.append('.')
        if ':' in word:
            s.append(word.replace(':', ''))
            s.append(':')
        if ';' in word:
            s.append(word.replace(';', ''))
            s.append(';')
        else:
            s.append(word)
    res = [l for l in node_phrase.split() if l in s]
    return " ".join(res)


wh_rules_patterns = get_rule_patterns(WH_RULES_PATH)


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
    tree = nltk.pos_tag(sentence.split())
    # print(tree)
    sent_dict = dict()

    for token in tree:
        sent_dict[token[1]] = token[0]

    questions = set()
    url = "http://localhost:9010/tregex"

    # if 'NNP' in sent_dict and 'VBZ' in sent_dict:
    #     questions.add("What does " + sent_dict['NNP'] + " " + get_lemma(sent_dict['VBZ'], 'v') + "?")

    answer_patterns = get_rule_patterns(ANSWER_POS_RULES)
    answer_nodes = []
    for pattern in answer_patterns:
        answer_nodes += get_tregex_matches(pattern, sentence, 'match')

    for pattern in wh_rules_patterns:
        request_params = {"pattern": pattern}
        r = requests.post(url, data=sentence.encode('utf-8'), params=request_params)
        if r.ok and '0' in r.json()['sentences'][0]:
            unmovable_nodes = r.json()['sentences'][0]['0']['namedNodes']
            for node in unmovable_nodes:
                if node['unmv'] in answer_nodes:
                    answer_nodes.remove(node['unmv'])

    answer_phrases = list(get_text_from_node(x, sentence) for x in answer_nodes)
    # print(answer_phrases)

    # verb_selector = get_tregex_matches(
    #     "ROOT < (S=clause < (VP=mainvp [ < (/VB.?/=tensed !< is|was|were|am|are|has|have|had|do|does|did)| < /VB.?/=tensed !< VP ]))",
    #     sentence, 'namedNodes')

    # print(corenlp.sNLP.parse(sentence))
    verb_selector = get_tregex_matches("VP > S", sentence, 'match')
    # print(verb_selector)
    noun_selector = get_tregex_matches("NP > S", sentence, 'match')

    max_l = ""
    for names in verb_selector:
        # print(names)

        main_verb_node = ""
        for name in names:
            # print(name['clause'])
            if 'mainvp' in name:
                main_verb_node = name['mainvp']

        # print(main_verb_node)
        # main_verb = get_text_from_node(main_verb_node, sentence)
        main_verb = get_text_from_node(names, sentence)

        if len(main_verb) > len(max_l):
            # nps = get_tregex_matches('NP', main_verb, 'match')
            # if len(nps) == 0:
            #     break
            # np = get_text_from_node(min(nps), main_verb)
            # print(np)

            verbs = get_tregex_matches('VB | VBD | VBG | VBN | VBP | VBZ', main_verb, 'match')
            verb = get_text_from_node(verbs[0], main_verb)
            # print(verb)

            max_l = main_verb
    for names in noun_selector:
        # print(names)
        noun = get_text_from_node(names, sentence)
        if noun not in max_l and noun in answer_phrases:
            noun_pos = corenlp.sNLP.pos(noun)[0][1]
            if noun_pos == "DT" or noun_pos == "PRP":
                questions.add("What " + max_l + "?")
                continue

            question_word = "What "
            ner_tag = ner.get_ner_tag(noun)
            if ner_tag != "O":
                if ner_tag == "PERSON":
                    question_word = "Who "
                elif ner_tag == "LOCATION":
                    question_word = "Where "
                elif ner_tag == "DATE":
                    question_word = "When "

            verb_lemma = get_lemma(verb, 'v')

            if verb_lemma == "be":
                questions.add("What " + verb + " " + get_lemma(noun, 'n') + "?")
            else:
                verb_pos = corenlp.sNLP.pos(verb)[0][1]
                second_word = "does"
                if verb_pos == "VBN" or verb_pos == "VBD":
                    second_word = "did"
                if verb_pos == "VBP":
                    second_word = "do"
                next_word_index = (sentence.split()).index(verb) + 1
                next_word = (sentence.split())[next_word_index]
                pos_tag = corenlp.sNLP.pos(next_word)[0]
                if pos_tag[1] == 'IN' or pos_tag[1] == 'TO' and pos_tag[0] != 'that':
                    questions.add(question_word + second_word + " " + noun.lower() + " " + verb_lemma + " " + pos_tag[0] + "?")
                else:
                    questions.add(question_word + second_word + " " + noun.lower() + " " + verb_lemma + "?")

    if len(questions) == 0:
        for answer_node in answer_nodes:
            text = get_text_from_node(answer_node, sentence)
            s = " " + sentence + " "
            if text in sentence.split():
                pos_tag = corenlp.sNLP.pos(text)[0][1]
                if ner.get_ner_tag(text) != "O" or pos_tag == 'CD':
                    questions.add(s.replace(' ' + text + ' ', ' __________________ '))
                    break

    for question in questions:
        print(sentence)
        print(question)
        print('-------------------------------------------------------------------------------------')
    return questions


def verb_id(sentence):
    aux_match = get_tregex_matches('ROOT=root < (S=clause <+(/VP.*/) (VP < /(MD|VB.?)/=aux < (VP < /VB.?/=verb)))',
                                   sentence,
                                   'aux')

    verb_match = get_tregex_matches('ROOT=root < (S=clause <+(/VP.*/) (VP < /(MD|VB.?)/=aux < (VP < /VB.?/=verb)))',
                                    sentence,
                                    'verb')

    # mverb_match = get_tregex_matches('ROOT < (S=clause < (VP=mainvp </VB.?/=tensed !< (VP < /VB.?/)))',
    #                                  sentence,
    #                                  'clause')

    third = get_tregex_matches('ROOT=root < (S=clause <+(/VP.*/) (VP <(/VB.?/=copula < is|are|was|were|am) !< VP))',
                               sentence,
                               'copula')


def generate_questions(sentences):
    questions = set()
    for sentence in sentences:
        sentence_questions = get_question(sentence.replace(".", ""))
        for q in sentence_questions:
            questions.add(q)
    return questions


if __name__ == "__main__":
    # from text_processing import text_prep

    # s = text_prep.get_ranked_sentences_lexrank("../text_processing/text_files/raw_input.txt")
    # generate_questions(s)
    # verb_id("John saw Mary.")
    print(corenlp.sNLP.pos("them"))
