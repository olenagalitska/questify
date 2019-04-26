from flask import Flask, render_template, request
import requests
from text_processing import text_prep, summarizer

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    text = ""
    ranked = []
    if request.method == "POST":

        text = request.form['input-text']
        text_prep.rewrite_file("text_processing/text_files/raw_input.txt", text)
        text = text_prep.sent_tokenize(text)
        # ranked = text_prep.get_ranked_sentences("text_processing/text_files/raw_input.txt")
        ranked = summarizer.generate_summary("text_processing/text_files/raw_input.txt")
        print(ranked)

    return render_template('index.html', text=text, ranked=ranked)


if __name__ == '__main__':
    app.run()
