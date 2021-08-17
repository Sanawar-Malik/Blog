




class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    username = db.Column(db.String(80),unique=True, nullable=False)
    password = db.Column(db.String(150))
    profile = db.Column(db.String(150), default='profile.jpg')
    email = db.Column(db.String(20), unique=True, nullable=False)

def __repr__(self):
        return '<User %r>' % self.username


