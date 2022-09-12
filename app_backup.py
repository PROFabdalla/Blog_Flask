from flask import Flask, request, jsonify, render_template, flash,redirect,url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, validators, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
from wtforms.widgets import TextArea
from flask_login import UserMixin , login_user , LoginManager , login_required , logout_user,current_user

app = Flask('__name__')
# data base config
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:@localhost/stock"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# the secret key
app.config['SECRET_KEY'] = "this is my key"

db = SQLAlchemy(app)
Migrate = Migrate(app, db)


login_manger = LoginManager()
login_manger.init_app(app)
login_manger.login_view='login'

@login_manger.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# return JSON files
@app.route('/date')
def get_date():
    # names = ["abdalla", "mohamed", "hazem", "salwa", "omar", "ali", "laila"]
    names = {"id":  123,
             "name":  "mohamed",
             "eamil":  "mohamed@gmil.com",
             "address":  "egypt",
             "phone":  1143306714,
             "password":  "12345qwe",
             "skils":  "css"}

    # return {"names": names}
    return names
    # return {"date": date.today()}

# -------------------------------- user model --------------------------------------
class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False,unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    favourate_color = db.Column(db.String(150))
    add_date = db.Column(db.DateTime, default=datetime.utcnow)
    password_hashed = db.Column(db.String(150))

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




class Nameform(FlaskForm):
    name = StringField("what is your name", validators=[
                       DataRequired(), validators.length(max=10)])
    submit = SubmitField("submit")


class Passwordform(FlaskForm):
    email = StringField("email", validators=[DataRequired()])
    password = PasswordField("password", validators=[DataRequired()])
    submit = SubmitField("submit")


class Userform(FlaskForm):
    username = StringField("User name", validators=[
                       DataRequired(), validators.length(max=20)])
    name = StringField("name", validators=[
                       DataRequired(), validators.length(max=20)])
    email = StringField("email", validators=[
                        DataRequired(), validators.length(max=50)])
    favourate_color = StringField("favorite color")
    password_hashed = PasswordField("password", validators=[DataRequired(
    ), EqualTo('password_hashed2', message='password must match!')])
    password_hashed2 = PasswordField(
        "confirm the password", validators=[DataRequired()])
    submit = SubmitField("submit")

class Loginform(FlaskForm):
    username= StringField("username",validators=[DataRequired()]) 
    password= PasswordField("password",validators=[DataRequired()]) 
    submit = SubmitField("submit")


# ----------------------------------- post model -----------------------------

class Posts(db.Model):
    id          = db.Column(db.Integer,primary_key=True)
    title       = db.Column(db.String(255))
    content     = db.Column(db.Text)
    auther      = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime,default=datetime.utcnow)
    slug        = db.Column(db.String(255))

class Postform(FlaskForm):
    title = StringField("title",validators=[DataRequired()])
    content = StringField("content",validators=[DataRequired()],widget=TextArea())
    auther = StringField("auther",validators=[DataRequired()])
    slug = StringField("slug",validators=[DataRequired()])
    submit = SubmitField("submit")


# ----------------------------------------------------- routes ------------------
@app.route('/')
def home():
    return render_template('home.html')


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500

# create new name profile
@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = Nameform()
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("the name submitted successfuly")

    return render_template('nameform.html', name=name, form=form)

# add new user
@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = Userform()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            hashed_pw = generate_password_hash(form.password_hashed.data)
            myuser = User(username=form.username.data,name=form.name.data, email=form.email.data,
                          favourate_color=form.favourate_color.data, password_hashed=hashed_pw)
            db.session.add(myuser)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.username.data = ''
        form.email.data = ''
        form.favourate_color.data = ''
        form.password_hashed.data = ''
        flash("user added successfuly!")
    our_users = User.query.order_by(User.add_date)

    return render_template('add_user.html', form=form, name=name, our_users=our_users)

# update user info
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_user(id):
    form = Userform()
    user_to_update = User.query.get_or_404(id)
    if request.method == "POST":
        user_to_update.name = request.form['name']
        user_to_update.email = request.form['email']
        user_to_update.favourate_color = request.form['favourate_color']
        user_to_update.username = request.form['username']
        try:
            db.session.commit()
            flash("user updated successfuly")
            return render_template('update.html', form=form, user_to_update=user_to_update)
        except:
            flash("user updated error!! try again")
            return render_template('update.html', form=form, user_to_update=user_to_update)

    else:
        return render_template('update.html', form=form, user_to_update=user_to_update)

# delete user
@app.route('/delete/<int:id>')
def delete(id):
    name = None
    form = Userform()
    user_del = User.query.get_or_404(id)
    try:
        db.session.delete(user_del)
        db.session.commit()
        flash("user added successfuly!")
        name = form.name.data
        our_users = User.query.order_by(User.add_date)
        return render_template('add_user.html', form=form, name=name, our_users=our_users)
    except:
        flash("oops something wrong!")
        return render_template('add_user.html', form=form, name=name, our_users=our_users)


# test email and password
@app.route('/test_pass', methods=['GET', 'POST'])
def test_pw():
    email = None
    password = None
    passed = None
    user_to_check = None
    form = Passwordform()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        form.email.data = ''
        form.password.data = ''
        user_to_check = User.query.filter_by(email=email).first()
        passed = check_password_hash(user_to_check.password_hashed, password)

    return render_template('test_password.html', email=email, password=password, user_to_check=user_to_check, passed=passed, form=form)


# adding new post
@app.route('/add-post',methods=['GET','POST'])
def add_post():
    form = Postform()
    if form.validate_on_submit():
        post = Posts(title=form.title.data,content=form.content.data,auther=form.auther.data,slug=form.slug.data)
        form.title.data=''
        form.content.data=''
        form.slug.data=''
        form.auther.data=''

        db.session.add(post)
        db.session.commit()
        flash("post added successfuly")
    return render_template("add_post.html",form=form)


#showing all posts
@app.route('/posts')
def posts():
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template('posts.html',posts=posts)

#showing spacific post
@app.route('/posts/<int:id>')
def get_post(id):
    post = Posts.query.get_or_404(id)
    return render_template('onepost.html',post=post)


#edite spacific post
@app.route('/post/<int:id>',methods=['GET','POST'])
@login_required
def edit_post(id):
    form = Postform()
    post = Posts.query.get_or_404(id)
    if form.validate_on_submit():
        post.title = form.title.data
        post.auther = form.auther.data
        post.slug   = form.slug.data
        post.content= form.content.data
        db.session.add(post)
        db.session.commit()
        flash("post has been updated successfuly")
        return redirect(url_for('get_post',id=post.id))

    form.title.data= post.title
    form.auther.data= post.auther
    form.slug.data= post.slug
    form.content.data= post.content
    return render_template('edit_post.html',form=form)



#delte spacific post
@app.route('/post/delete/<int:id>')
@login_required
def delete_post(id):
    post = Posts.query.get_or_404(id)
    try:
        db.session.delete(post)
        db.session.commit()
        flash("the post deleted successfully")
        return redirect(url_for('posts'))
    except:
        flash("oops! some thing wronge during the deleting")
        return redirect(url_for('posts'))


#login
@app.route('/login',methods=['GET','POST'])
def login():
    form = Loginform()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password_hashed,form.password.data):
                login_user(user)
                flash("login successfull")
                return redirect(url_for('dashboard'))
            else:
                flash("wrong password")
        else:
            flash("this user dosent exist!!")
    return render_template('login.html',form=form)


#dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


#logout
@app.route('/logout',methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    flash("you loged out we are welcome to see you again ")
    return redirect(url_for('login'))



if __name__ == "__main__":
    app.run(debug=True)
