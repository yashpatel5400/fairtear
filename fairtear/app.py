"""
__author__ = Yash Patel and Zachary Liu
__name__   = app.py
__description__ = Main Flask application server
"""

import os
from flask import Flask, request, redirect, url_for, render_template, jsonify, abort
from werkzeug.utils import secure_filename

from fairtear.forms import DataForm
from fairtear.compile import compile, fair_prove

app = Flask(__name__)
app.config.from_object("config")

def allowed_file(filename):
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]

def save_file(file):
    filename = os.path.join(app.config["UPLOAD_FOLDER"], secure_filename(file.filename))
    file.save(filename)
    return filename

def prepare_attribute(form_data):
    return [form_data[value] for value in ['attribute', 'conditional', 'threshold']]

@app.route('/_analyze_data', methods=["GET","POST"])
def analyze_data():
    form = DataForm()

    if not form.enable_qualified.data:
        del form.qualified

    if not form.validate():
        return jsonify(errors=form.errors)

    x_csv = save_file(form.xcsv.data)
    clf_pickle = save_file(form.clf.data)

    outfr = "fairtear/output/result.fr"
    sensitive_attrs = [prepare_attribute(form.sensitive.data)]
    if form.enable_qualified.data:
        qualified_attrs = [prepare_attribute(form.qualified.data)]
    else:
        qualified_attrs = []
    fairness_targets = [prepare_attribute(form.target.data)]
    compile(clf_pickle, x_csv, form.target.data['attribute'], outfr, sensitive_attrs, qualified_attrs, fairness_targets)
    result = fair_prove(outfr)
    return jsonify(errors=None, result=result)

@app.route("/", methods=["GET", "POST"])
def upload_file():
    form = DataForm(request.form)
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

    return render_template("index.html", form=form)