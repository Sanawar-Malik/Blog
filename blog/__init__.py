
from enum import unique
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import defaultload

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password@127.0.0.1/Newblog'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


from blog import routes