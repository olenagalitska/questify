from nlp import corenlp, tregex
from nlp.ner import ner
from nltk.stem.wordnet import WordNetLemmatizer
import nltk

WH_RULES_PATH = '/Users/olenagalitska/Developer/questify/question_generation/rules/wh_rules.txt'
ANSWER_POS_RULES = '/Users/olenagalitska/Developer/questify/question_generation/rules/answer_pos.txt'
REMOVE_FROM_S = '/Users/olenagalitska/Developer/questify/question_generation/rules/remove.txt'

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
    if ner_tag is not None:
        if ner_tag[1] == "PERSON":
            question_word = "Who "
        elif ner_tag[1] == "LOCATION":
            question_word = "Where "
        elif ner_tag[1] == "DATE":
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
    # print(corenlp.sNLP.parse(verb_phrase))
    verbs = tregex.get_tregex_matches('VB | VBD | VBG | VBN | VBP | VBZ >> VP >> S', verb_phrase, 'match')
    # verbs = tregex.get_tregex_matches('VP', verb_phrase, 'match')
    # for verb in verbs:
    #     print(tregex.get_text_from_node(verb, verb_phrase))
    # else:
    candidate = verb_phrase.split()[0]
    if corenlp.sNLP.pos(candidate) == "MD":
        return candidate + verb_phrase.split()[1]
    else:
        return candidate


def lower_np(noun_phrase):
    w = noun_phrase.split()[0]
    if ner.get_ner_tag(w) is None:
        noun_phrase = noun_phrase.replace(w, w.lower())
    return noun_phrase


def get_question(verb_phrase, noun, sentence):
    noun_pos_tag = corenlp.sNLP.pos(noun)[0][1]
    if noun_pos_tag == "DT" or noun_pos_tag == "WDT":
        return "What " + verb_phrase + "?"
    elif noun_pos_tag == "PRP":
        return "Who " + verb_phrase + "?"

    noun = lower_np(noun)

    next_noun = verb_phrase
    answers = get_answer_phrases(verb_phrase)
    for word in verb_phrase.split():
        if word in answers:
            next_noun = word
            break
    question_word = get_question_word(next_noun)

    verb = get_main_verb(verb_phrase)

    # transform verb
    verb_lemma = get_lemma(verb, 'v')

    relation = (verb_lemma, noun, verb_phrase.replace(verb, ""))
    # print(relation)

    if verb_lemma == "be":
        return "What " + verb + " " + noun + "?"

    else:
        second_word = get_second_word(verb)
        next_word_index = (sentence.split()).index(verb) + 1
        if next_word_index < len(sentence.split()):
            next_word = (sentence.split())[next_word_index]
            next_pos_tag = corenlp.sNLP.pos(next_word)[0]
            if (next_pos_tag[1] == 'IN' or next_pos_tag[1] == 'TO') and next_pos_tag[0] != 'that':
                return question_word + second_word + " " + noun + " " + verb_lemma + " " + next_pos_tag[0] + "?"
        return question_word + second_word + " " + noun + " " + verb_lemma + "?"


def get_questions(sentence):
    questions = set()

    # get possible answer phrases for sentence
    answer_phrases = get_answer_phrases(sentence)

    # select main verb and noun phrases
    verb_selector = tregex.get_tregex_matches("VP > (S > ROOT)", sentence, 'match')
    max_verb_phrase = ""
    for match in verb_selector:
        verb_candidate = tregex.get_text_from_node(match, sentence)
        if len(verb_candidate) > len(max_verb_phrase):
            max_verb_phrase = verb_candidate

    noun_selector = tregex.get_tregex_matches("NP > (S > ROOT)", sentence, 'match')
    for match in noun_selector:
        noun = tregex.get_text_from_node(match, sentence)

        if noun in answer_phrases and noun not in max_verb_phrase:
            new_question = get_question(max_verb_phrase, noun, sentence)
            if new_question != "":
                questions.add(new_question)

    if len(questions) == 0:
        for answer_phrase in answer_phrases:
            if answer_phrase not in sentence:
                continue
            questions.add(sentence.replace(answer_phrase, ' __________________ '))

    for question in questions:
        print(sentence)
        # print(corenlp.sNLP.parse(sentence))
        print(question)
        print('-------------------------------------------------------------------------------------')
    return questions


def clean_sentence(sentence):
    patterns = tregex.get_rule_patterns(REMOVE_FROM_S)

    nodes_to_remove = []
    for pattern in patterns:
        nodes_to_remove += tregex.get_tregex_matches(pattern, sentence, 'match')

    for node in nodes_to_remove:
        print(node)


def generate_questions(sentences):
    questions = list()
    for sentence in sentences:
        sentence_questions = get_questions(sentence.replace(".", ""))
        for q in sentence_questions:
            questions.append(q)
    return set(questions)


if __name__ == "__main__":
    print(corenlp.sNLP.parse("He sailed away from this small ice-covered island to a great big ice-covered island"))
