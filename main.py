from text_processing import text_prep
from question_generation.q_generator import generate_questions
from nltk import sent_tokenize
from text_processing.simplify import simplify_text

FILE_PATH = "text_processing/text_files/complex_sentences.txt"

if __name__ == "__main__":
    sentences = text_prep.get_ranked_sentences_lexrank(FILE_PATH)
    # sentences = nltk.sent_tokenize(text_prep.read_file_to_string(FILE_PATH))
    # text = text_prep.read_file_to_string()
    simple_text = simplify_text("\n".join(sentences))
    questions = generate_questions(sent_tokenize(simple_text))

    # print("\n".join(questions))


