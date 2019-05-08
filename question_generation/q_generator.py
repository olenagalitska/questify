import nltk
import requests
from question_generation import ner, corenlp
from nltk.stem.wordnet import WordNetLemmatizer

WH_RULES_PATH = '/Users/olenagalitska/Developer/questify/question_generation/wh_rules.txt'
ANSWER_POS_RULES = '/Users/olenagalitska/Developer/questify/question_generation/answer_pos.txt'


def get_rule_patterns(path):
    file = open(path, 'r')
    p = file.readlines()
    file.close()
    return p


wh_rules_patterns = get_rule_patterns(WH_RULES_PATH)


def get_lemma(word, w_type):
    return WordNetLemmatizer().lemmatize(word, w_type)


def get_text_from_node(node, sentence):
    node_phrase = node.replace(')', ' ')

    s = list()
    for word in sentence.split():
        for post_p in ',.;:)]}':
            if post_p in word:
                s.append(word.replace(post_p, ''))
                s.append(post_p)
            else:
                s.append(word)

        for pre_p in '({[':
            if pre_p in word:
                s.append(word.replace(pre_p, ''))
                s.append(pre_p)
            else:
                s.append(word)

    res = [l for l in node_phrase.split() if l in s]
    return " ".join(res)


def get_tregex_matches(pattern, sentence, key_name):
    result = list()
    url = "http://localhost:9010/tregex"
    r = requests.post(url, data=sentence.encode('utf-8'), params={"pattern": pattern})
    if r.ok:
        for s in r.json()['sentences']:
            for key, value in s.items():
                result.append(value[key_name])
    return result


def get_answer_phrases(sentence):
    answer_patterns = get_rule_patterns(ANSWER_POS_RULES)
    answer_nodes = []
    for pattern in answer_patterns:
        answer_nodes += get_tregex_matches(pattern, sentence, 'match')

    for pattern in wh_rules_patterns:
        unmovable_nodes_matches = get_tregex_matches(pattern, sentence, 'namedNodes')
        for match in unmovable_nodes_matches:
            node = match[0]
            if node['unmv'] in answer_nodes:
                answer_nodes.remove(node['unmv'])

    return list(get_text_from_node(x, sentence) for x in answer_nodes)


def get_question_word(noun):
    question_word = "What "
    ner_tag = ner.get_ner_tag(noun)
    if ner_tag != "O":
        if ner_tag == "PERSON":
            question_word = "Who "
        elif ner_tag == "LOCATION":
            question_word = "Where "
        elif ner_tag == "DATE":
            question_word = "When "
    return question_word


def get_second_word(verb):
    verb_pos_tag = corenlp.sNLP.pos(verb)[0][1]
    second_word = "does"
    if verb_pos_tag == "VBN" or verb_pos_tag == "VBD":
        second_word = "did"
    if verb_pos_tag == "VBP":
        second_word = "do"
    return second_word


def get_main_verb(verb_phrase):
    verbs = get_tregex_matches('VB | VBD | VBG | VBN | VBP | VBZ', verb_phrase, 'match')
    if len(verbs) != 0:
        return get_text_from_node(verbs[0], verb_phrase)
    else:
        return verb_phrase


def get_question(verb_phrase, noun, sentence):
    question = ""
    verb = get_main_verb(verb_phrase)
    noun_pos_tag = corenlp.sNLP.pos(noun)[0][1]
    if noun_pos_tag == "DT" or noun_pos_tag == "PRP":
        question = "What " + verb_phrase + "?"

    # determine question word
    question_word = get_question_word(noun)

    # transform verb
    verb_lemma = get_lemma(verb, 'v')

    if verb_lemma == "be":
        question = "What " + verb + " " + noun + "?"

    else:
        second_word = get_second_word(verb)
        next_word_index = (sentence.split()).index(verb) + 1
        next_word = (sentence.split())[next_word_index]
        next_pos_tag = corenlp.sNLP.pos(next_word)[0]
        if next_pos_tag[1] == 'IN' or next_pos_tag[1] == 'TO' and next_pos_tag[0] != 'that':
            question = question_word + second_word + " " + noun + " " + verb_lemma + " " + next_pos_tag[0] + "?"
        else:
            question = question_word + second_word + " " + noun + " " + verb_lemma + "?"

    return question


def get_questions(sentence):
    questions = set()

    # get possible answer phrases for sentence
    answer_phrases = get_answer_phrases(sentence)

    # select main verb and noun phrases
    verb_selector = get_tregex_matches("VP > S", sentence, 'match')
    max_verb_phrase = ""
    for match in verb_selector:
        verb_candidate = get_text_from_node(match, sentence)
        if len(verb_candidate) > len(max_verb_phrase):
            max_verb_phrase = verb_candidate

    noun_selector = get_tregex_matches("NP > S", sentence, 'match')
    for match in noun_selector:
        noun = get_text_from_node(match, sentence)

        if noun in answer_phrases and noun not in max_verb_phrase:
            new_question = get_question(max_verb_phrase, noun, sentence)
            if new_question != "":
                questions.add(new_question)

    if len(questions) == 0:
        for answer_phrase in answer_phrases:
            questions.add(sentence.replace(' ' + answer_phrase + ' ', ' __________________ '))

    for question in questions:
        print(sentence)
        print(question)
        print('-------------------------------------------------------------------------------------')
    return questions


def generate_questions(sentences):
    questions = set()
    for sentence in sentences:
        sentence_questions = get_questions(sentence.replace(".", ""))
        for q in sentence_questions:
            questions.add(q)
    return questions


if __name__ == "__main__":
    print(corenlp.sNLP.pos("them"))
