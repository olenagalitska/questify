from text_processing import text_prep
from question_generation import q_generator, simplify_sentence
import nltk

FILE_PATH = "text_processing/text_files/raw_input.txt"

if __name__ == "__main__":
    # print(text_prep.read_file_to_string(FILE_PATH))
    # sentences = text_prep.get_ranked_sentences_lexrank(FILE_PATH)
    # print(sentences)
    sentences = nltk.sent_tokenize(text_prep.read_file_to_string(FILE_PATH))
    for sentence in sentences:
        print("-------------------------------------------")
        print(sentence)
        simplify_sentence.simplify(sentence)

    # questions = q_generator.generate_questions(sentences)
    # for question in questions:
    #     print(questions)


