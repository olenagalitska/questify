# from rake_nltk import Rake, Metric
from lexrank import STOPWORDS, LexRank
from nltk.tokenize import sent_tokenize
from math import floor
# from textteaser import TextTeaser


def read_file_to_string(filepath):
    f = open(filepath, 'r')
    content = f.read()
    f.close()
    return content


def read_file_to_array(filepath):
    f = open(filepath, 'r')
    content = f.readlines()
    f.close()
    return content


def rewrite_file(filepath, content):
    f = open(filepath, 'w')
    f.write(content)
    f.close()


def get_ranked_sentences_lexrank(filepath):
    raw_text = list()
    raw_text.append(read_file_to_array(filepath))
    lxr = LexRank(raw_text, stopwords=STOPWORDS['en'])
    sentences = sent_tokenize(read_file_to_string(filepath))
    summary_sentences = lxr.get_summary(sentences, summary_size=floor(len(sentences) / 2), threshold=.1)
    return summary_sentences


# def get_ranked_sentences_textteaser(filepath):
#     raw_text = read_file_to_string(filepath)
    # tt = TextTeaser()
    # return tt.summarize("", raw_text)


if __name__ == '__main__':
    summary = get_ranked_sentences_lexrank("text_files/raw_input.txt")
    for sent in summary:
        print(sent)
