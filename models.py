from app import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


# -------------------------------- user model --------------------------------------
class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    username = db.Column(db.String(20), nullable=False,unique=True)
    email = db.Column(db.String(200), nullable=False, unique=True)
    favourate_color = db.Column(db.String(150))
    about_auther = db.Column(db.Text(500),nullable=True)
    add_date = db.Column(db.DateTime, default=datetime.utcnow)
    password_hashed = db.Column(db.String(150))
    profile_pic = db.Column(db.String(120),nullable=True)
    postes          = db.relationship('Posts',backref='poster')

    @property
    def password(self):
        raise AttributeError("password is not readable!")

    @password.setter
    def password(self, password):
        self.password_hashed = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hashed, password)

    def __repr__(self):
        return '<Name %r>' % self.name





# ----------------------------------- post model -----------------------------

class Posts(db.Model):
    id          = db.Column(db.Integer,primary_key=True)
    title       = db.Column(db.String(255))
    content     = db.Column(db.Text)
    # auther      = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime,default=datetime.utcnow)
    slug        = db.Column(db.String(255))
    poster_id   = db.Column(db.Integer,db.ForeignKey('user.id'))

