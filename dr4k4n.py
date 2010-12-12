#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from flaskext.sqlalchemy import SQLAlchemy
from hashlib import md5

SECRET_KEY = 'VERYS3CR3T!'
DEBUG = True
HOST = '127.0.0.1'

ADMIN_USERNAME = 'Dr4K4n'
ADMIN_PASSWORD = 'changeme'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('DR4K4N_SETTINGS', silent=True)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://dr4k4n:dr4k4n@localhost/dr4k4n'
db = SQLAlchemy(app)

# DB Models
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    _password = db.Column(db.String(32), nullable=False)
    email = db.Column(db.String(60), nullable=False, unique=True)
    
    def __init__(self, username, email, password=u''):
        self.username = username
        self.email = email
        self.password = password
    
    def _set_password(self, password):
        self._password = md5(password).hexdigest()
    
    def _get_password(self):
        return self._password
    
    password = property(_get_password,_set_password)

    def check_password(self, password):
        print self.password
        print md5(password).hexdigest()
        return self.password == md5(password).hexdigest()
        
    def __repr__(self):
        return '<User %r>' % self.username

class BlogPost(db.Model):
    __tablename__ = 'blogposts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    shorttext = db.Column(db.Text, nullable=False)
    longtext = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    
    def __init__(self, title, author_id, shorttext, longtext):
        self.title = title;
        self.author_id = author_id;
        self.shorttext = shorttext;
        self.longtext = longtext;
    
    def __repr__(self):
        return '<BlogPost %r>' % self.id

# static pages
@app.route('/')
def home():
    return render_template('main.html')

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')
    
@app.route('/impressum')
def impressum():
    return render_template('impressum.html')

# login / logout    
@app.route('/login',methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] == ADMIN_USERNAME and request.form['password'] == ADMIN_PASSWORD:
            flash(u'Tach Chef!')
            session['logged_in'] = True
            session['admin'] = True
            session['user_id'] = 1
        else:
            print request.form['password']
            user = User.query.filter_by(username=request.form['username']).first()
            print user
            if user and user.check_password(request.form['password']):
                session['logged_in'] = True
                session['user_id'] = user.id
                flash(u'Moinsen')
                return redirect(url_for('show_tree'))
            else:
                error = u'Öhm... verkehrt :-('
        
    return render_template('login.html', error=error)    

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash(u'Auf wiedersehen :)')
    return redirect(url_for('home')) 
 

# admin menu 
@app.route('/admin') 
def admin():
    if not session.get('logged_in'):
        flash(u'ohne Login wird das aber nix...')
        return redirect(url_for('login'))
    if not session.get('admin'):
        flash(u'Hier haste nix verloren - husch husch !')        
        return redirect(url_for('home'))
        
    return render_template('admin.html')

# user verwaltung
@app.route('/user/verwalten')
def user_verwalten():
    if not session.get('logged_in'):        
        flash(u'ohne Login wird das aber nix...')
        return redirect(url_for('login'))
    
    users = User.query.all()
    
    return render_template('user_verwalten.html', users=users)

@app.route('/user/new',methods=['GET', 'POST'])
def user_new():
    if not session.get('logged_in'):        
        flash(u'ohne Login wird das aber nix...')
        return redirect(url_for('login'))
    
    if not request.form:
        return render_template('user_new.html');    
 
    newUser = User(request.form['username'], request.form['email'], request.form['password'])
    db.session.add(newUser)
    db.session.commit()
    
    flash(u'nice one - is drin ;-)')
    return redirect(url_for('admin'))

 
@app.route('/user/<int:user_id>/edit',methods=['GET'])
def user_edit(user_id):
    if not session.get('logged_in'):        
        flash(u'ohne Login wird das aber nix...')
        return redirect(url_for('login'))
        
    user = User.query.get(user_id)
    
    if user is None:
        flash(u'Bidde? den kennsch ned!')
        return redirect(url_for('admin'))
    
    return render_template('user_edit.html',user=user);

@app.route('/user/<int:user_id>/del',methods=['GET'])
def user_del(user_id):
    if not session.get('logged_in'):        
        flash(u'ohne Login wird das aber nix...')
        return redirect(url_for('login'))
        
    user = User.query.get(user_id)
    
    if user is None:
        flash(u'Bidde? den kennsch ned!')
        return redirect(url_for('admin'))
    
    db.session.delete(user)
    db.session.commit()
    
    flash(u'Atze entfernt')
    return redirect(url_for('admin'))

# blog verwaltung
@app.route('/bloggen/verwalten')
def bloggen_verwalten():
    if not session.get('logged_in'):        
        flash(u'ohne Login wird das aber nix...')
        return redirect(url_for('login'))
    
    blogPosts = BlogPost.query.all()
    
    return render_template('bloggen_verwalten.html', blogPosts=blogPosts)

@app.route('/bloggen/new',methods=['GET', 'POST'])
def bloggen_new():
    if not session.get('logged_in'):        
        flash(u'ohne Login wird das aber nix...')
        return redirect(url_for('login'))
    
    if not request.form:
        return render_template('bloggen_new.html');
    
    newPost = BlogPost(request.form['title'], session['user_id'], request.form['shorttext'], request.form['longtext'])
    db.session.add(newPost)
    db.session.commit()
    flash(u'nice one - is drin ;-)')
    return redirect(url_for('admin'))
 
@app.route('/bloggen/<int:post_id>/edit',methods=['GET', 'POST'])
def bloggen_edit(post_id):
    if not session.get('logged_in'):        
        flash(u'ohne Login wird das aber nix...')
        return redirect(url_for('login'))
        
    post = BlogPost.query.get(post_id)
    
    if post is None:
        flash(u'Bidde? den kennsch ned!')
        return redirect(url_for('admin'))
    
    return render_template('bloggen_edit.html',post=post);

@app.route('/bloggen/<int:post_id>/del',methods=['GET', 'POST'])
def bloggen_del(post_id):
    if not session.get('logged_in'):        
        flash(u'ohne Login wird das aber nix...')
        return redirect(url_for('login'))
        
    post = BlogPost.query.get(post_id)
    
    if post is None:
        flash(u'Bidde? den kennsch ned!')
        return redirect(url_for('admin'))
    
    db.session.delete(post)
    db.session.commit()
    
    flash(u'Post entfernt')
    return redirect(url_for('admin'))

# start
if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'],host=app.config['HOST'])
