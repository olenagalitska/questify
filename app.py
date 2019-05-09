from flask import Flask, render_template, request
from text_processing import text_prep
from question_generation import q_generator

app = Flask(__name__)

ranked = []
FILE_PATH = "text_processing/text_files/raw_input.txt"


@app.route('/', methods=['GET', 'POST'])
def index():
    text = ""
    matched = ""
    if request.method == "POST":
        text = request.form['input-text']
        # text = text.encode('utf-8')
        text_prep.rewrite_file(FILE_PATH, text)
        text = text_prep.sent_tokenize(text)
        global ranked
        ranked = text_prep.get_ranked_sentences_lexrank(FILE_PATH)
    return render_template('index.html', text=text, ranked=ranked)


@app.route('/get_questions')
def questify():
    questions = q_generator.generate_questions(ranked)

    return 'questions'


if __name__ == '__main__':
    app.run()
