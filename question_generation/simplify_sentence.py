from question_generation import corenlp, q_generator
import requests

RULES_PATH = "/Users/olenagalitska/Developer/questify/question_generation/simple_rules.txt"


def get_text_from_node(node, sentence):
    node_phrase = node.replace(')', ' ')
    sentence = sentence.replace(',', '')
    sentence = sentence.replace('.', '')
    res = [l for l in node_phrase.split() if l in sentence.split()]
    return " ".join(res)


def delete_pp(s):
    # dependencies = corenlp.sNLP.dependency_parse(s)
    # for dep in dependencies:
    #     print(dep)
    #     s_arr = s.split()
    #     s_arr.append(".")
    #     print(s_arr[dep[1]])
    #     print(s_arr[dep[2]])


    pps = []
    url = "http://localhost:9010/tregex"
    pattern = "PP"
    r = requests.post(url, data=s.encode('utf-8'), params={"pattern": pattern})
    selector = r.json()['sentences'][0]
    for match in selector:
        node = selector[match]['match']
        text = get_text_from_node(node, s)
        pps.append(text)

    for pp in pps:
        s = s.replace(" " + pp + " ", " ")

    return s


def simplify(sentence):
    result = sentence
    file = open(RULES_PATH, 'r')
    patterns = file.readlines()
    file.close()
    url = "http://localhost:9010/tregex"

    for pattern in patterns:
        r = requests.post(url, data=sentence.encode('utf-8'), params={"pattern": pattern})
        sentences = r.json()['sentences']
        for s in sentences:
            for key, value in s.items():
                nodes = value['namedNodes']
                for node in nodes:

                    if 'finite' in node:
                        result = get_text_from_node(node['finite'], sentence)
    return result

def elem_sentences(sentence):
    np_nodes = q_generator.get_tregex_matches("NP", sentence, 'match')
    vb_nodes = q_generator.get_tregex_matches("VP", sentence, 'match')
    pp_nodes = q_generator.get_tregex_matches("PP", sentence, 'match')

    nps, vbs, pps = list(), list(), list()

    for node in np_nodes:
        nps.append(get_text_from_node(node, sentence))
    for node in vb_nodes:
        vbs.append(get_text_from_node(node, sentence))
    for node in pp_nodes:
        pps.append(get_text_from_node(node, sentence))

    print(nps)
    print(vbs)
    print(pps)


if __name__ == '__main__':
    sentence = "People who live in Scotland are called Scots."
    elem_sentences(sentence.replace(".", ""))
