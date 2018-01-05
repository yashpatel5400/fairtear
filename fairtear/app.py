"""
__author__ = Yash Patel and Zachary Liu
__name__   = app.py
__description__ = Main Flask application server
"""

import os
from flask import Flask, request, redirect, url_for, render_template, jsonify
from werkzeug.utils import secure_filename

from fairtear.forms import DataForm
from fairtear.compile import compile

app = Flask(__name__)
app.config.from_object("config")

def allowed_file(filename):
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]

@app.route('/_analyze_data', methods=["POST"])
def analyze_data():
    form = DataForm(request.form)
    if request.method == "POST" and form.validate():
        # check if the post request has the file part
        form_filenames = ["xcsv","ycsv","clf"]
        files = []

        for filename in form_filenames:
            if filename not in request.files:
                return redirect(request.url)

        files = [request.files[filename] for filename in form_filenames]
        
        # if user does not select file, browser also
        # submit a empty part without filename
        for file in files:
            if not file or file.filename == "" or not allowed_file(file.filename):
                return redirect(request.url)

        filenames = []
        for file in files:
            filename = os.path.join(app.config["UPLOAD_FOLDER"], 
                secure_filename(file.filename))
            filenames.append(filename)
            file.save(filename)

        sensitive_attrs_dict  = {}
        qualified_attrs_dict  = {}
        fairness_targets_dict = {}
        for key in request.form:
            attribute_vals = key.split("_")
            if len(attribute_vals) != 3:
                continue
            
            attr_type, attr_val, attr_count = attribute_vals
            if   attr_type == "sensitive": target_dict = sensitive_attrs_dict
            elif attr_type == "qualified": target_dict = qualified_attrs_dict
            elif attr_type == "fairness" : target_dict = fairness_targets_dict
            else: continue
            
            if attr_count not in target_dict:
                target_dict[attr_count] = [None, None, None]

            if   attr_val == "attribute"  : target_ind = 0
            elif attr_val == "conditional": target_ind = 1
            elif attr_val == "threshold"  : target_ind = 2
            else: continue

            target_dict[attr_count][target_ind] = request.form[key]

        sensitive_attrs  = sensitive_attrs_dict.values()
        qualified_attrs  = qualified_attrs_dict.values()
        fairness_targets = fairness_targets_dict.values()

        x_csv, y_csv, clf_pickle = filenames
        outfr = "fairtear/output/result.fr"
        compile(clf_pickle, x_csv, y_csv, outfr, sensitive_attrs, 
            qualified_attrs, fairness_targets)

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