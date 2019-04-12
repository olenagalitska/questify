from flask import Flask, render_template, request
import requests
from text_processing import text_prep

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    text = ""
    if request.method == "POST":
        print(request.form['input-text'])
        text = request.form['input-text']

        text_prep.rewrite_file("text_processing/text_files/raw_input.txt", text)
        text = text_prep.get_ranked_words("text_processing/text_files/raw_input.txt")

    return render_template('index.html', text=text)


if __name__ == '__main__':
    app.run()
