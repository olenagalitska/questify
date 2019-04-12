from rake_nltk import Rake, Metric


def read_file_to_string(filepath):
    f = open(filepath, 'r')
    content = f.read()
    f.close()
    return content


def rewrite_file(filepath, content):
    f = open(filepath, 'w')
    f.write(content)
    f.close()


def get_ranked_words(filepath):
    raw_text = read_file_to_string(filepath)

    r = Rake(min_length=1, max_length=1,
             ranking_metric=Metric.WORD_DEGREE)  # Uses stopwords for english from NLTK, and all puntuation characters.
    r.extract_keywords_from_text(raw_text)
    return(r.get_ranked_phrases())


if __name__ == '__main__':
    rewrite_file("text_files/raw_input.txt", "why?")
    print(read_file_to_string("text_files/raw_input.txt"))
