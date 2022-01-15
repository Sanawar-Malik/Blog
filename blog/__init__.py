from enum import unique
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import defaultload
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://cubyvuagxwfclm:56b5c2b18cab7094573a4f56d847a11fcaf27008ef74ca133a72ee8c15820679@ec2-3-227-15-75.compute-1.amazonaws.com:5432/d7pnbn7vkiv9a2'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'MALIK'
db = SQLAlchemy(app)
bcrypt=Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"


from blog import routes