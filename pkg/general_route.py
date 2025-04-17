from flask import render_template, url_for,flash,redirect

from pkg import app

@app.route("/")
def general_route():
    return render_template('index.html')