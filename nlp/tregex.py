import requests


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


def get_rule_patterns(path):
    file = open(path, 'r')
    p = file.readlines()
    file.close()
    return p
