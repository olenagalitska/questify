from nlp import tregex
from nlp.corenlp import sNLP as nlp
from nlp.ner import ner
from nltk.stem.wordnet import WordNetLemmatizer
import nltk
from text_processing.text_prep import read_file_to_string, replace
from text_processing import simplify

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

    return list((tregex.get_text_from_node(x, sentence), x) for x in answer_nodes)


def get_second_word(verb):
    verb_pos_tag = nlp.pos(verb)[0][1]
    second_word = "does"
    if verb_pos_tag == "VBN" or verb_pos_tag == "VBD":
        second_word = "did"
    if verb_pos_tag == "VBP":
        second_word = "do"
    return second_word


def lower_np(noun_phrase):
    w = noun_phrase.split()[0]
    if ner.get_ner_tag(w) is None:
        noun_phrase = replace(w, w.lower(), noun_phrase)
    return noun_phrase


def get_questions(sentence):
    questions = set()

    answer_phrases = get_answer_phrases(sentence)

    vp_s = tregex.get_tregex_matches("(/VB.?/ !> (/VB.?/ > VP )) > (VP > (S > ROOT))", sentence, 'match')

    for answer in answer_phrases:
        question_word = "WHAT / WHO "
        answer_type = replace("(", "", answer[1].split()[0])
        if answer_type == "PP":
            if "(IN like)" in answer[1] or "(IN as)" in answer[1]:
                question_word = "HOW "
            elif "(IN for)" in answer[1] and 'QP' in answer[1]:
                question_word = "FOR HOW LONG "
            elif ("IN" in answer[1] and "CD" in answer[1]) or ("(IN while)" in answer[1]):
                question_word = "WHEN "
            elif "(TO to)" in answer[1] or ("IN" in answer[1] and "CD" not in answer[1]):
                question_word = "WHERE "

        if len(vp_s) == 0:
            question = sentence.replace(answer[0], "_________________")
            questions.add(question)
            continue

        verb_node = vp_s[0]
        verb = tregex.get_text_from_node(verb_node, sentence)

        verb_lemma = get_lemma(verb, 'v')

        remainder = replace('.', "", replace(answer[0], "", sentence))
        remainder = lower_np(remainder)

        if verb_lemma == "be":
            question = question_word + " " + verb + " " + replace(verb, '', remainder) + "?"
            questions.add(question)

        else:
            if remainder.split()[0] == verb:
                question = question_word + " " + remainder + "?"
                questions.add(question)
                continue
            remainder = replace(verb, verb_lemma, remainder)
            second_word = get_second_word(verb)
            question = question_word + " " + second_word + " " + remainder + "?"
            questions.add(question)
    return questions


def generate_questions(input_sentences):
    questions = list()
    for sentence in input_sentences:
        print(sentence)
        sentence_questions = get_questions(sentence)
        for q in sentence_questions:
            print('> ', q)
            questions.append(q)
        print('---------------------------------------------------------------')
    return set(questions)


if __name__ == "__main__":
    sentences = nltk.sent_tokenize(
        read_file_to_string("/Users/olenagalitska/Developer/questify/text_processing/text_files/complex_sentences.txt"))
    simple_text = simplify.simplify_text("\n".join(sentences))
    generate_questions(nltk.sent_tokenize(simple_text))
