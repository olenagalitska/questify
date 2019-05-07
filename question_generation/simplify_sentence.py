from question_generation import corenlp
import requests

RULES_PATH = "/Users/olenagalitska/Developer/questify/question_generation/simple_rules.txt"


def get_text_from_node(node, sentence):
    node_phrase = node.replace(')', ' ')
    sentence = sentence.replace(',', '')
    sentence = sentence.replace('.', '')
    res = [l for l in node_phrase.split() if l in sentence.split()]
    return " ".join(res)


def simplify(sentence):
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
                    print(node)

                    if 'finite' in node:
                        print(get_text_from_node(node['finite'], sentence))


if __name__ == '__main__':
    sentence = "Although it will probably never be known whether this woman was the Grand Duchess Anastasia, her search to establish her identity has been the subject of numerous books, plays, and movies."
    file = open(RULES_PATH, 'r')
    patterns = file.readlines()
    file.close()
    url = "http://localhost:9010/tregex"

    for pattern in patterns:
        r = requests.post(url, data=sentence.encode('utf-8'), params={"pattern": pattern})
        sentences = r.json()['sentences']
        for s in sentences:
            for key, value in s.items():
                node = value['namedNodes'][0]
                print(value['namedNodes'])

                if 'finite' in node:
                    print(get_text_from_node(node['finite'], sentence))

                # else:
                #     noun = node['noun']
                #     rel = node['rel']
                # print(get_text_from_node(noun, sentence) + " " + get_text_from_node(rel, sentence))
