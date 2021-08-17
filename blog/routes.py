from flask import Flask, render_template
from blog import app, db


@app.route("/")
def index():
    return render_template('index.html')



