from text_processing import text_prep
from question_generation import q_generator
import nltk

FILE_PATH = "text_processing/text_files/raw_input.txt"

if __name__ == "__main__":
    # sentences = text_prep.get_ranked_sentences_lexrank(FILE_PATH)
    sentences = nltk.sent_tokenize(text_prep.read_file_to_string(FILE_PATH))

    questions = q_generator.generate_questions(sentences)


