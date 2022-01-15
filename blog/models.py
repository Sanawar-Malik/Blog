from datetime import datetime
from blog import db, login_manager
from flask_login import UserMixin

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
