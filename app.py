from PIL import Image
from flask import Flask, render_template, request, flash, redirect, sessions, url_for, current_app
from flask.helpers import flash
from flask_login import login_user,login_required, current_user, logout_user
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
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Length, EqualTo, Email, DataRequired,  ValidationError
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from flask_migrate import Migrate
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'MALIK'
db = SQLAlchemy(app)
migrate=Migrate(app, db)
bcrypt=Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80),unique=True, nullable=False)
    password_hash = db.Column(db.String(150))
    image_file = db.Column(db.String(150), nullable=False, default='default.jpg')
    email_address = db.Column(db.String(20), unique=True, nullable=False)
    date = db.Column(db.DateTime, nullable=False,default=datetime.utcnow)
    posts = db.relationship('Post', backref='user', lazy='dynamic',cascade="all,delete")
    comments = db.relationship('Comment', backref='user',lazy='dynamic',cascade="all,delete")
    def __repr__(self):
        return '<User %r>' % self.username
    @property
    def password(self):
        return self.password
    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')  
    def check_password_correction(self, attempted_password):
       return bcrypt.check_password_hash(self.password_hash, attempted_password)
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
class RegisterForm(FlaskForm):
    def validate_username(self, username_to_check):
       user = User.query.filter_by(username=username_to_check.data).first()
       if user:
           raise ValidationError('Username already exists! Please try a different username')
    def validate_email_address(self, email_address_to_check):
        email_address = User.query.filter_by(email_address=email_address_to_check.data).first()
        if email_address:
            raise ValidationError('Email Address already exists! Please try a different email address')
    username = StringField(label='User Name:', validators=[Length(min=2, max=30), DataRequired()])
    email_address = StringField(label='Email Address:', validators=[Email(), DataRequired()])
    password1 = PasswordField(label='Password:', validators=[Length(min=6), DataRequired()])
    password2 = PasswordField(label='Confirm Password:', validators=[EqualTo('password1'), DataRequired()])
    submit = SubmitField(label='Register')
class LoginForm(FlaskForm):
    username = StringField(label='User Name:', validators=[DataRequired()])
    password = PasswordField(label='Password:', validators=[DataRequired()])
    submit = SubmitField(label='Login')    

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
    return render_template('home.html', params=params, posts=posts, prev=prev, next=next, user=user)
@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data, email_address=form.email_address.data, password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f"Account created successfully! You are now logged in as {user_to_create.username}", category='success')
        return redirect(url_for('home'))
    if form.errors != {}: #If there are not errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')
    return render_template('register.html', form=form)
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('home'))
        else:
            flash('Username and password are not match! Please try again', category='danger')
    return render_template('login.html', form=form)
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

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login_page'))
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
        current_user.email_address = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email_address
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',image_file=image_file, form=form)



if __name__ == '__main__':
    app.run(debug=True)
