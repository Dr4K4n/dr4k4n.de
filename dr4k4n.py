#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from flaskext.sqlalchemy import SQLAlchemy

SECRET_KEY = 'VERYS3CR3T!'
DEBUG = True
HOST = '127.0.0.1'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('DR4K4N_SETTINGS', silent=True)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://dr4k4n:dr4k4n@localhost/dr4k4n'
db = SQLAlchemy(app)

# DB Models

# currently none

@app.route('/')
def home():
    return render_template('main.html')

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')
    
@app.route('/impressum')
def impressum():
    return render_template('impressum.html')
    
if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'],host=app.config['HOST'])
