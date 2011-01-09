#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from flaskext.sqlalchemy import SQLAlchemy
from hashlib import md5
from twython import Twython

SECRET_KEY = 'VERYS3CR3T!'
DEBUG = True
HOST = '0.0.0.0'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('DR4K4N_SETTINGS', silent=True)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://dr4k4n:dr4k4n@localhost/dr4k4n'
db = SQLAlchemy(app)

twitter = Twython()

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
    post_id = db.Column(db.Integer, db.ForeignKey('blogposts.id'))
    post = db.relationship(BlogPost, uselist=False, backref=db.backref('commentPost',cascade="none"))
    comment = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    
    def __init__(self, post_id, author_id, comment):
		self.post_id = post_id
		self.author_id = author_id
		self.comment = comment

    def getComment(self):
        return unicode.replace(self.comment,'\n','<br>')	
        
    def __repr__(self):
        return '<Comment %r>' % self.id

# main pages
@app.route('/')
def home():
    posts = BlogPost.query.limit(10).all()
    return render_template('main.html', current='home', posts=posts)

@app.route('/read/<int:post_id>', methods=['GET','POST'])
def read_post(post_id):
    if request.form and request.form['comment'] != "":
		comment = Comment(post_id,session['user_id'],request.form['comment'])
		db.session.add(comment)
		db.session.commit()
		flash(u'Danke für deinen Kommentar')		
    post = BlogPost.query.get(post_id)
    comments = Comment.query.filter(Comment.post_id == post.id).all()
    logged_in = ('user_id' in session)
    return render_template('read.html', current='home', post=post, comments=comments, logged_in=logged_in)

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
				return redirect(url_for('intern'))
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
    if len(q) > 2:
        posts = BlogPost.query.from_statement('SELECT * FROM blogposts WHERE title LIKE "%user%"').all()
    else:        
        flash('Leider nix gefunden... hast du mindestens 3 Zeichen eingegeben ?')
        posts = []
    return render_template('search.html', current='home', posts=posts)

# admin menu 
@app.route('/intern') 
def intern():
    if not session.get('logged_in'):
        flash(u'ohne Login wird das aber nix...')
        return redirect(url_for('login'))

    return render_template('intern.html', current='intern', admin=session.get('admin'))

# user verwaltung
@app.route('/user/verwalten')
def user_verwalten():
    if not session.get('logged_in'):        
        flash(u'ohne Login wird das aber nix...')
        return redirect(url_for('login'))
    if not session.get('admin'):
        flash(u'pöse!!!')
        return redirect(url_for('home'))
    
    users = User.query.all()
    
    return render_template('user_verwalten.html', current='intern', users=users)

@app.route('/user/new',methods=['GET', 'POST'])
def user_new():
    if not session.get('logged_in'):        
        flash(u'ohne Login wird das aber nix...')
        return redirect(url_for('login'))
    if not session.get('admin'):
        flash(u'pöse!!!')
        return redirect(url_for('home'))
        
    if not request.form:
        return render_template('user_new.html', current='intern');    
    
    newUserAdmin = 0
    if 'admin' in request.form and request.form['admin'] == 'on':
        newUserAdmin = 1

    newUser = User(request.form['username'], request.form['email'], request.form['password'], newUserAdmin)

    db.session.add(newUser)
    db.session.commit()
    
    flash(u'nice one - is drin ;-)')
    return redirect(url_for('intern'))

@app.route('/user/<int:user_id>/edit',methods=['GET','POST'])
def user_edit(user_id):
    if not session.get('logged_in'):        
        flash(u'ohne Login wird das aber nix...')
        return redirect(url_for('login'))
    if not session.get('admin'):
        flash(u'pöse!!!')
        return redirect(url_for('home'))
                
    user = User.query.get(user_id)
    newUser = user
    
    if user is None:
        flash(u'Bidde? den kennsch ned!')
        return redirect(url_for('intern'))
    
    if request.form:
        editUserAdmin = 0
        if 'admin' in request.form and request.form['admin'] == 'on':
            editUserAdmin = 1
        if request.form['password'] != "":
            user.password = request.form['password']
        user.username = request.form['username']
        user.email = request.form['email']
        user.admin = editUserAdmin
        db.session.commit()
        flash(u'check! Hab ich')
        return redirect(url_for('intern'))
        
    return render_template('user_edit.html', current='intern',user=user);

@app.route('/user/<int:user_id>/del',methods=['GET'])
def user_del(user_id):
    if not session.get('logged_in'):        
        flash(u'ohne Login wird das aber nix...')
        return redirect(url_for('login'))
    if not session.get('admin'):
        flash(u'pöse!!!')
        return redirect(url_for('home'))
                
    user = User.query.get(user_id)
    
    if user is None:
        flash(u'Bidde? den kennsch ned!')
        return redirect(url_for('intern'))
    
    db.session.delete(user)
    db.session.commit()
    
    flash(u'Atze entfernt')
    return redirect(url_for('intern'))

# blog verwaltung
@app.route('/bloggen/verwalten')
def bloggen_verwalten():
    if not session.get('logged_in'):        
        flash(u'ohne Login wird das aber nix...')
        return redirect(url_for('login'))
    
    blogPosts = BlogPost.query.all()
    
    return render_template('bloggen_verwalten.html', current='intern', blogPosts=blogPosts)

@app.route('/bloggen/new',methods=['GET', 'POST'])
def bloggen_new():
    if not session.get('logged_in'):        
        flash(u'ohne Login wird das aber nix...')
        return redirect(url_for('login'))
    
    if not request.form:
        return render_template('bloggen_new.html', current='intern');
    
    newPost = BlogPost(request.form['title'], session['user_id'], request.form['shorttext'], request.form['longtext'])
    db.session.add(newPost)
    db.session.commit()
    flash(u'nice one - is drin ;-)')
    return redirect(url_for('intern'))
 
@app.route('/bloggen/<int:post_id>/edit',methods=['GET', 'POST'])
def bloggen_edit(post_id):
    if not session.get('logged_in'):        
        flash(u'ohne Login wird das aber nix...')
        return redirect(url_for('login'))
        
    post = BlogPost.query.get(post_id)

    if post is None:
        flash(u'Bidde? den kennsch ned!')
        return redirect(url_for('intern'))
    
    if request.form:
        post.title = request.form['title']
        post.shorttext = request.form['shorttext']
        post.longtext = request.form['longtext']
        db.session.commit()
        flash(u'check! Hab ich')
        return redirect(url_for('intern'))  
    
    return render_template('bloggen_edit.html', current='intern', post=post);

@app.route('/bloggen/<int:post_id>/del',methods=['GET', 'POST'])
def bloggen_del(post_id):
    if not session.get('logged_in'):        
        flash(u'ohne Login wird das aber nix...')
        return redirect(url_for('login'))
        
    post = BlogPost.query.get(post_id)
    
    if post is None:
        flash(u'Bidde? den kennsch ned!')
        return redirect(url_for('intern'))
    
    db.session.delete(post)
    db.session.commit()
    
    flash(u'Post entfernt')
    return redirect(url_for('intern'))

@app.route('/backend/getTweets')
def get_tweets():
	tweetsAll = twitter.getUserTimeline(screen_name='Dr4K4n')
	tweets = []
	t_i = 0
	for t in tweetsAll:
		if t_i > 9:
			break
		tweets.append([t['id'],t['text']])
		t_i += 1
	return render_template('backend/tweets.html', tweets=tweets)
	
# start
if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'],host=app.config['HOST'])
