"""
__author__ = Yash Patel and Zachary Liu
__name__   = app.py
__description__ = Main Flask application server
"""

import os
from flask import Flask, request, redirect, url_for, render_template, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config.from_object("config")

def allowed_file(filename):
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]

@app.route('/_analyze_data', methods=["GET", "POST"])
def analyze_data():
    print(request['xcsv'])
    xcsv = request.args.get('xcsv', 0)
    ycsv = request.args.get('ycsv', 0)
    clf  = request.args.get('clf', 0)

    return jsonify(result=a + b)

@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        # check if the post request has the file part
        filenames = ["xcsv","ycsv","clf"]
        files = []

        for filename in filenames:
            if filename not in request.files:
                return redirect(request.url)

        files = [request.files[filename] for filename in filenames]
        
        # if user does not select file, browser also
        # submit a empty part without filename
        for file in files:
            if not file or file.filename == "" or not allowed_file(file.filename):
                return redirect(request.url)

        for file in files:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

    return render_template("index.html")

@app.route("/test")
def test():
    return render_template("test.html")