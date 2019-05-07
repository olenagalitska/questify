from flask import Flask, render_template, request
import requests
from text_processing import text_prep, summarizer
import subprocess
from question_generation import q_generator

app = Flask(__name__)

ranked = []


@app.route('/', methods=['GET', 'POST'])
def index():
    text = ""
    matched = ""
    if request.method == "POST":
        text = request.form['input-text']
        # text = text.encode('utf-8')
        text_prep.rewrite_file("text_processing/text_files/raw_input.txt", text)
        text = text_prep.sent_tokenize(text)
        # ranked = text_prep.get_ranked_sentences("text_processing/text_files/raw_input.txt")
        global ranked
        ranked = summarizer.generate_summary("text_processing/text_files/raw_input.txt")
    return render_template('index.html', text=text, ranked=ranked)


@app.route('/get_questions')
def questify():
    questions = q_generator.generate_questions(ranked)

    return 'questions'


if __name__ == '__main__':
    # java_command = 'java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -annotators "tokenize,ssplit,pos,lemma,parse,sentiment" -port 9000 -timeout 30000'.split()
    # print(java_command)
    # subprocess.call(['cd', 'stanford-corenlp'] + java_command)
    app.run()
