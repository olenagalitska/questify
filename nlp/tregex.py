import requests


def get_text_from_node(node, sentence):
    node_phrase = node.replace(')', ' ')
    node_phrase = [x for x in node_phrase.split() if not (x[0] == '(' and len(x) > 1)]
    res = [l for l in node_phrase if l in sentence]
    text = ""
    for w in res:
        if w in ",.;:'\"?!]})":
            text += w
        else:
            text += " " + w
    return text[1:]


def get_tregex_matches(pattern, sentence, key_name):
    result = list()
    url = "http://localhost:9010/tregex"
    r = requests.post(url, data=sentence.encode('utf-8'), params={"pattern": pattern})
    if r.ok:
        for s in r.json()['sentences']:
            for key, value in s.items():
                result.append(value[key_name])
    return result


def get_rule_patterns(path):
    file = open(path, 'r')
    p = file.readlines()
    file.close()
    return p
