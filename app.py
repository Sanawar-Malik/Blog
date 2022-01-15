from PIL import Image
from flask import Flask, render_template, request, flash, redirect, sessions, url_for, current_app
from flask.helpers import flash
from flask_login import login_user,login_required, current_user, logout_user
from form import UpdateAccountForm
from werkzeug.utils import secure_filename
import json
import secrets
import os
import math
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import defaultload
from flask_bcrypt import Bcrypt,bcrypt
from flask_login import LoginManager,login_manager
from datetime import datetime
from flask_login import UserMixin
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password@localhost/Appblog'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'MALIK'
db = SQLAlchemy(app)
bcrypt=Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = 'info'
# postgres://cubyvuagxwfclm:56b5c2b18cab7094573a4f56d847a11fcaf27008ef74ca133a72ee8c15820679@ec2-3-227-15-75.compute-1.amazonaws.com:5432/d7pnbn7vkiv9a2

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80),unique=True, nullable=False)
    password = db.Column(db.String(150))
    image_file = db.Column(db.String(150), nullable=False, default='default.jpg')
    email = db.Column(db.String(20), unique=True, nullable=False)
    date = db.Column(db.DateTime, nullable=False,default=datetime.utcnow)
    posts = db.relationship('Post', backref='user', lazy='dynamic',cascade="all,delete")
    comments = db.relationship('Comment', backref='user',lazy='dynamic',cascade="all,delete")
    def __repr__(self):
        return '<User %r>' % self.username
    
class Post(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(180), nullable=False)
    body = db.Column(db.Text, nullable=False)
    comments = db.Column(db.Integer, default=0)
    views = db.Column(db.Integer, default=0)
    author = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)
    comments = db.relationship('Comment',backref='post', lazy=True,cascade="all,delete")
    pub_date = db.Column(db.DateTime, nullable=False,default=datetime.utcnow)
    def __repr__(self):
        return '<Post %r>' % self.title
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    author = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    date_pub = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return '<Comment %r' % self.name


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')
    
    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')    


with open('config.json', 'r') as c:
    params = json.load(c)["params"]
@app.route("/")
@app.route("/home")
def home():
    user = User.query.all()
    posts = Post.query.order_by(Post.id.desc()).all()
    last = math.ceil(len(posts)/int(params['no_of_posts']))
    page = request.args.get('page')
    if (not str(page).isnumeric()):
        page = 1
    page = int(page)
    posts = posts[(page-1)*int(params['no_of_posts']):(page-1)*int(params['no_of_posts'])+ int(params['no_of_posts'])]
    if page==1:
        prev = "#"
        next = "/?page="+ str(page+1)
    elif page==last:
        prev = "/?page="+ str(page-1)
        next = "#"
    else:
        prev = "/?page="+ str(page-1)
        next = "/?page="+ str(page+1)
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('home.html', params=params, posts=posts, prev=prev, next=next, user=user, image_file=image_file)
@app.route('/about')
def about():
    return render_template('about.html')
@app.route('/comment/<int:post_id>', methods=['POST','GET'])
def posts( post_id):
    post = Post.query.get_or_404(post_id)
    posts = Post.query.order_by(Post.id.desc()).all()
    comments = Comment.query.filter_by(post_id=post.id).all()
    post.views += 1
    db.session.commit()
    if request.method =="POST":
        message = request.form.get('message') 
        comment = Comment(message=message, author=current_user.id,post_id=post.id)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been submited  submitted will be published after aproval of admin', 'success')
        return redirect(request.url)
    return render_template('single.html', post=post, posts=posts, comments=comments)
@app.route('/post/<int:post_id>/', methods=['POST', 'GET'])
def page(post_id):
    post = Post.query.get_or_404(post_id)
    posts = Post.query.order_by(Post.id.desc()).all()
    return render_template('single.html', post=post, posts=posts)
@app.route('/updatepost/<int:id>', methods=['POST', 'GET'])
@login_required
def updatepost(id):
    post = Post.query.get_or_404(id)
    if request.method=="POST":
        post.title = request.form.get('title')
        post.body= request.form.get('body')
        db.session.commit()
        flash('Your post has been Update','success')
        return redirect(url_for('home'))
    return render_template('updatepost.html', post=post)
@app.route('/delete/<int:id>', methods=['POST', 'GET'])
@login_required
def delete(id):
    post = Post.query.filter_by(id=id).first()
    db.session.delete(post)
    flash('Your post has been deleted','success')    
    db.session.commit()
    return redirect(url_for('dashboard'))
@app.route('/delcomment/<int:id>')
@login_required
def delcomment(id):
    comment = Comment.query.get_or_404(id)
    db.session.delete(comment)
    db.session.commit()
    flash('Comment has deleted ','success')
    return redirect(url_for('admin'))
@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method=="POST":
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user:
            flash('The username already exist!','warning')
            return redirect(url_for('register'))
        email = User.query.filter_by(email=request.form.get('email')).first()
        if email:
            flash('The email already exist!','warning') 
            return redirect(url_for('register'))  
        username = request.form.get("username")  
        email = request.form.get("email")  
        password = request.form.get("password")
        repeat_password = request.form.get("repeat_password")           
        if password != repeat_password:
            flash("Password does not match please try again",'warning')
            return redirect(url_for('register'))
        password_has = bcrypt.generate_password_hash(password)    
        users = User(username=username, email=email, password=password_has) 
        db.session.add(users)
        db.session.commit() 
        flash("Thanks for registration",'success')
        return redirect(url_for('login'))                  
    return render_template('register.html')
@app.route('/login', methods=['GET', 'POST'])
def login():    
    if request.method=='POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and bcrypt.check_password_hash(user.password, request.form.get('password')):
            login_user(user)
            flash('Logged in successfully.', 'success')
            next = request.args.get('next')
            return redirect(next or url_for('home'))
        flash('Username and password does not match, please try again','danger')    
    return render_template('login.html')
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
@app.route("/dashboard")
@login_required
def dashboard():
    our_users = User.query.all()
    users = User.query.get(current_user.id)
    posts = users.posts.all()
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('dashboard.html', posts=posts, our_users=our_users,image_file=image_file)  
@app.route("/post",  methods=['GET', 'POST'])
@login_required
def addpost():
    if request.method=="POST":
        title = request.form.get('title')
        body= request.form.get('body')
        post = Post(title=title, body=body,author=current_user.id)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been submited','success')
        return redirect('home')
    return render_template('addpost.html',post=Post.query.all())
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn
@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',image_file=image_file, form=form)



if __name__ == '__main__':
    app.run(debug=True)
