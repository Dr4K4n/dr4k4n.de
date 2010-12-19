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
    admin = db.Column(db.Boolean)
    
    def __init__(self, username, email, password, admin):
        self.username = username
        self.email = email
        self.password = password
        self.admin = admin
    
    def _set_password(self, password):
        self._password = md5(password).hexdigest()
    
    def _get_password(self):
        return self._password
    
    password = property(_get_password,_set_password)

    def check_password(self, password):
        print self.password
        print md5(password).hexdigest()
        return self.password == md5(password).hexdigest()
    
    def is_admin(self):
        return admin
    
    def __repr__(self):
        return '<User %r>' % self.username

class BlogPost(db.Model):
    __tablename__ = 'blogposts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author = db.relationship(User, uselist=False, backref=db.backref('BlogPoster',cascade="none"))
    shorttext = db.Column(db.Text, nullable=False)
    longtext = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    
    def __init__(self, title, author_id, shorttext, longtext):
        self.title = title;
        self.author_id = author_id;
        self.shorttext = shorttext;
        self.longtext = longtext;
    
    def getShorttext(self):
        return unicode.replace(self.shorttext,'\n','<br>')
        
    def getText(self):
        return unicode.replace(self.shorttext + self.longtext,'\n','<br>')
    
    def __repr__(self):
        return '<BlogPost %r>' % self.id

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author = db.relationship(User, uselist=False, backref=db.backref('commentUsers',cascade="none"))
    comment = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    
    def __init__(self, author, comment, date):
        self.author = author
        self.comment = comment
        self.date = date
    
    def __repr__(self):
        return '<Comment %r>' % self.id

# static pages
@app.route('/')
def home():
    posts = BlogPost.query.limit(10).all()
    return render_template('main.html', current='home', posts=posts)

@app.route('/read/<int:post_id>')
def read_post(post_id):
    post = BlogPost.query.get(post_id)
    return render_template('read.html', current='home', post=post)

@app.route('/gallery')
def gallery():
    return render_template('gallery.html', current='gallery')
    
@app.route('/impressum')
def impressum():
    return render_template('impressum.html', current='impressum')

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
            user = User.query.filter_by(username=request.form['username']).first()
            if user and user.check_password(request.form['password']):
                session['logged_in'] = True
                session['user_id'] = user.id
                session['admin'] = user.admin
                if user.admin:
                    flash(u'Moinsen')
                    return redirect(url_for('home'))
                else:
                    flash(u'Tach Chef!')
                    return redirect(url_for('admin'))
            else:
                error = u'Öhm... verkehrt :-('
        
    return render_template('login.html', current='login', error=error)    

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash(u'Auf wiedersehen :)')
    return redirect(url_for('home')) 

# search
@app.route('/search',methods=['GET'])
def search():
    q = request.args.get('q')
    if len(q) > 3:
        posts = BlogPost.query.from_statement('SELECT * FROM blogposts WHERE title LIKE "%user%"').all()
    else:        
        flash('Leider nix gefunden... hast du mindestens 3 Zeichen eingegeben ?')
        posts = []
    return render_template('search.html', current='home', posts=posts)

# admin menu 
@app.route('/admin') 
def admin():
    if not session.get('logged_in'):
        flash(u'ohne Login wird das aber nix...')
        return redirect(url_for('login'))
    if not session.get('admin'):
        flash(u'Hier haste nix verloren - husch husch !')        
        return redirect(url_for('home'))
        
    return render_template('admin.html', current='admin')

# user verwaltung
@app.route('/user/verwalten')
def user_verwalten():
    if not session.get('logged_in'):        
        flash(u'ohne Login wird das aber nix...')
        return redirect(url_for('login'))
    
    users = User.query.all()
    
    return render_template('user_verwalten.html', current='admin', users=users)

@app.route('/user/new',methods=['GET', 'POST'])
def user_new():
    if not session.get('logged_in'):        
        flash(u'ohne Login wird das aber nix...')
        return redirect(url_for('login'))
    
    if not request.form:
        return render_template('user_new.html', current='admin');    
    
    print '1'
    
    newUserAdmin = 0
    if 'admin' in request.form and request.form['admin'] == 'on':
        newUserAdmin = 1
    
    print '2'
     
    newUser = User(request.form['username'], request.form['email'], request.form['password'], newUserAdmin)
    
    print '3'
    
    db.session.add(newUser)
    db.session.commit()
    
    flash(u'nice one - is drin ;-)')
    return redirect(url_for('admin'))

@app.route('/user/<int:user_id>/edit',methods=['GET','POST'])
def user_edit(user_id):
    if not session.get('logged_in'):        
        flash(u'ohne Login wird das aber nix...')
        return redirect(url_for('login'))
        
    user = User.query.get(user_id)
    newUser = user
    
    if user is None:
        flash(u'Bidde? den kennsch ned!')
        return redirect(url_for('admin'))
    
    if request.form:
        editUserAdmin = 0
        if 'admin' in request.form and request.form['admin'] == 'on':
            editUserAdmin = 1
        if request.form['password'] != "":
            user.password = request.form['password']
        user.username = request.form['username']
        user.email = request.form['email']
        user.admin = newUserAdmin
        db.session.commit()
        flash(u'check! Hab ich')
        return redirect(url_for('admin'))
        
    return render_template('user_edit.html', current='admin',user=user);

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
    
    return render_template('bloggen_verwalten.html', current='admin', blogPosts=blogPosts)

@app.route('/bloggen/new',methods=['GET', 'POST'])
def bloggen_new():
    if not session.get('logged_in'):        
        flash(u'ohne Login wird das aber nix...')
        return redirect(url_for('login'))
    
    if not request.form:
        return render_template('bloggen_new.html', current='admin');
    
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
    
    if request.form:
        post.title = request.form['title']
        post.shorttext = request.form['shorttext']
        post.longtext = request.form['longtext']
        db.session.commit()
        flash(u'check! Hab ich')
        return redirect(url_for('admin'))  
    
    return render_template('bloggen_edit.html', current='admin', post=post);

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
