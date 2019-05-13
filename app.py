from flask import Flask, render_template, request
from text_processing import text_prep, simplify
from question_generation import q_generator
import pdfkit

app = Flask(__name__)

ranked = []
questions = []

FILE_PATH = "text_processing/text_files/raw_input.txt"


@app.route('/', methods=['GET', 'POST'])
def index():
    text = ""
    if request.method == "POST":
        text = request.form['input-text']
        text_prep.rewrite_file(FILE_PATH, text)
        text = simplify.simplify_text(text)
        global ranked
        ranked = text_prep.sent_tokenize(text)
    return render_template('index.html', text=text, ranked=ranked)


@app.route('/get_questions')
def questify():
    global questions
    questions = q_generator.generate_questions(ranked)
    html = render_template('questions.html', questions=questions)
    return html


if __name__ == '__main__':
    app.run()
