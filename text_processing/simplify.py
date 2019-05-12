from nlp import tregex
from nltk import sent_tokenize
from text_processing.text_prep import read_file_to_string, replace


def get_names_dict(r, s):
    results = tregex.get_tregex_matches(r, s, 'namedNodes')
    names = dict()
    for match in results:
        for name in match:
            names.update(name)
    return names


def try_remove(sent, pattern, *node_names, sentences):
    new_sent = sent
    names = get_names_dict(pattern, sent)
    if 'conj' in names:
        value = tregex.get_text_from_node(names['conj'], sent)
        index = sent.index(value)
        sentences.append(replace(",", ".", sent[:index]))
        sentences.append(sent[index + len(value) + 1:])
        return
    for name in node_names:
        if name in names:
            value = tregex.get_text_from_node(names[name], sent)
            new_sent = replace(value, "", new_sent)

    if new_sent != sent:
        sentences.append(new_sent)


def construct_noun_copula_app(sent, sentences):
    rule = "NP !< CC !< CONJP < (NP=noun $..(/,/ $.. (NP=app $.. /,/)))"
    names = get_names_dict(rule, sent)

    if "app" in names and "noun" in names:
        app = tregex.get_text_from_node(names['app'], sent)
        noun = tregex.get_text_from_node(names['noun'], sent)
        new_sent = noun + " is " + app + "."
        sentences.append(new_sent)


def construct_noun_copula_modifier(sent, sentences):
    rule = "NP=noun > NP $.. VP=modifier"
    names = get_names_dict(rule, sent)
    if "noun" in names and "modifier" in names:
        modifier = tregex.get_text_from_node(names['modifier'], sent)
        noun = tregex.get_text_from_node(names['noun'], sent)
        new_sent = noun + " was " + modifier + "."
        sentences.append(new_sent)


def construct_finite(sent, sentences):
    rule = "S=finite !>> NP|PP < NP < (VP < VBP|VB|VBZ|VBD|MD) ?< /\\./=punct"
    names = get_names_dict(rule, sent)
    if 'finite' in names:
        new_sent = (tregex.get_text_from_node(names['finite'], sent) + ".").replace('..', '.')
        if new_sent != sent:
            sentences.append(new_sent)


def extract_rel(sent, sentences):
    rule = "NP=noun > NP $.. (SBAR < S=rel !< WHADVP !< WHADJP)"
    names = get_names_dict(rule, sent)
    if 'rel' in names and 'noun' in names:
        rel = tregex.get_text_from_node(names['rel'], sent)
        noun = tregex.get_text_from_node(names['noun'], sent)
        # print(rel, "| ", noun)
        sentences.append(noun + " " + rel + ".")


def simplify_sentence(sentence):
    sentences = []
    try_remove(sentence, "ROOT < (S < CC=conj)", 'conj', sentences=sentences)
    try_remove(sentence, "ROOT < (S < (/[ˆ,]/=adjunct $.. (/,/ $.. VP)))", 'adjunct', sentences=sentences)
    try_remove(sentence, "SBAR|VP|NP=app $, /,/=lead $. /,/=trail !$ CC !$ CONJP", 'app', 'lead', 'trail',
               sentences=sentences)
    construct_noun_copula_app(sentence, sentences)
    construct_finite(sentence, sentences)
    construct_noun_copula_modifier(sentence, sentences)
    extract_rel(sentence, sentences)

    if len(sentences) == 0:
        sentences.append(sentence)

    return set(sentences)


def simplify_text(text):
    simplified_text = ""
    for snt in sent_tokenize(text):
        simple_s = "\n".join(x[0].upper() + x[1:] for x in simplify_sentence(snt))
        simplified_text += simple_s
        simplified_text += '\n'

    return simplified_text


if __name__ == "__main__":
    # simplify_text(
    #     read_file_to_string("/Users/olenagalitska/Developer/questify/text_processing/text_files/complex_sentences.txt"))
    s = simplify_sentence("My ESL teacher, who came to Germany in 1986, likes to ride his mountain bike.")
    print("\n".join(s))
