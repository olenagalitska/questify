import nltk
import requests
from question_generation import ner, corenlp, tregex
from nltk.stem.wordnet import WordNetLemmatizer

WH_RULES_PATH = '/Users/olenagalitska/Developer/questify/question_generation/wh_rules.txt'
ANSWER_POS_RULES = '/Users/olenagalitska/Developer/questify/question_generation/answer_pos.txt'

wh_rules_patterns = tregex.get_rule_patterns(WH_RULES_PATH)


def get_lemma(word, w_type):
    return WordNetLemmatizer().lemmatize(word, w_type)


def get_answer_phrases(sentence):
    answer_patterns = tregex.get_rule_patterns(ANSWER_POS_RULES)
    answer_nodes = []
    for pattern in answer_patterns:
        answer_nodes += tregex.get_tregex_matches(pattern, sentence, 'match')

    for pattern in wh_rules_patterns:
        unmovable_nodes_matches = tregex.get_tregex_matches(pattern, sentence, 'namedNodes')
        for match in unmovable_nodes_matches:
            node = match[0]
            if node['unmv'] in answer_nodes:
                answer_nodes.remove(node['unmv'])

    return list(tregex.get_text_from_node(x, sentence) for x in answer_nodes)


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
    verbs = tregex.get_tregex_matches('VB | VBD | VBG | VBN | VBP | VBZ', verb_phrase, 'match')
    if len(verbs) != 0:
        return tregex.get_text_from_node(verbs[0], verb_phrase)
    else:
        return verb_phrase


def lower_np(noun_phrase):
    for w in noun_phrase.split():
        if ner.get_ner_tag(w) is None:
            noun_phrase = noun_phrase.replace(w, w.lower())
    return noun_phrase


def get_question(verb_phrase, noun, sentence):
    noun_pos_tag = corenlp.sNLP.pos(noun)[0][1]
    if noun_pos_tag == "DT" or noun_pos_tag == "PRP":
        return "What " + verb_phrase + "?"
    noun = lower_np(noun)

    # determine question word
    question_word = get_question_word(noun)

    verb = get_main_verb(verb_phrase)

    # transform verb
    verb_lemma = get_lemma(verb, 'v')

    if verb_lemma == "be":
        return "What " + verb + " " + noun + "?"

    else:
        second_word = get_second_word(verb)
        next_word_index = (sentence.split()).index(verb) + 1
        next_word = (sentence.split())[next_word_index]
        next_pos_tag = corenlp.sNLP.pos(next_word)[0]
        if next_pos_tag[1] == 'IN' or next_pos_tag[1] == 'TO' and next_pos_tag[0] != 'that':
            return question_word + second_word + " " + noun + " " + verb_lemma + " " + next_pos_tag[0] + "?"
        else:
            return question_word + second_word + " " + noun + " " + verb_lemma + "?"


def get_questions(sentence):
    questions = set()

    # get possible answer phrases for sentence
    answer_phrases = get_answer_phrases(sentence)

    # select main verb and noun phrases
    verb_selector = tregex.get_tregex_matches("VP > S", sentence, 'match')
    max_verb_phrase = ""
    for match in verb_selector:
        verb_candidate = tregex.get_text_from_node(match, sentence)
        if len(verb_candidate) > len(max_verb_phrase):
            max_verb_phrase = verb_candidate

    noun_selector = tregex.get_tregex_matches("NP > S", sentence, 'match')
    for match in noun_selector:
        noun = tregex.get_text_from_node(match, sentence)

        if noun in answer_phrases and noun not in max_verb_phrase:
            new_question = get_question(max_verb_phrase, noun, sentence)
            if new_question != "":
                questions.add(new_question)

    if len(questions) == 0:
        for answer_phrase in answer_phrases:
            questions.add(sentence.replace(answer_phrase, ' __________________ '))

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
    phrase = "Love George Bush"
    for word in phrase.split():
        print(ner.get_ner_tag(word))
        if ner.get_ner_tag(word) is None:
            phrase = phrase.replace(word, word.lower())
    print(phrase)
