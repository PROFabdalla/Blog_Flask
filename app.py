from flask import Flask, request, jsonify, render_template, flash,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
from flask_login import UserMixin , login_user , LoginManager , login_required , logout_user,current_user
from webforms import Loginform,Nameform,Passwordform,Postform,Userform,Searchform,Commentform
from flask_ckeditor import CKEditor
from werkzeug.utils import secure_filename
import uuid as uuid
import os





app = Flask('__name__')
# data base config
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:@localhost/stock"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# the secret key
app.config['SECRET_KEY'] = "this is my key"


UPLOAD_FOLDER = 'static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# installing app
db = SQLAlchemy(app)
Migrate = Migrate(app, db)
ckeditor = CKEditor(app)



login_manger = LoginManager()
login_manger.init_app(app)
login_manger.login_view='login'

@login_manger.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



# context 
@app.context_processor
def base():
    form = Searchform()
    return dict(form=form)


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
    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(200), nullable=False)
    username        = db.Column(db.String(20), nullable=False,unique=True)
    email           = db.Column(db.String(200), nullable=False, unique=True)
    favourate_color = db.Column(db.String(150))
    about_auther    = db.Column(db.Text(500),nullable=True)
    add_date        = db.Column(db.DateTime, default=datetime.utcnow)
    password_hashed = db.Column(db.String(150))
    profile_pic     = db.Column(db.String(120),nullable=True)
    postes          = db.relationship('Posts',backref='poster')
    comments        = db.relationship('Comments',backref='commenter')

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
    post_pic    = db.Column(db.String(120),nullable=True)
    comments    = db.relationship('Comments',backref='comments')


# ----------------------------------- post model -----------------------------

class Comments(db.Model):
    id          = db.Column(db.Integer,primary_key=True)
    content     = db.Column(db.Text)
    date_posted = db.Column(db.DateTime,default=datetime.utcnow)
    post_id     = db.Column(db.Integer,db.ForeignKey('posts.id'))
    commnter_id = db.Column(db.Integer,db.ForeignKey('user.id'))





# ----------------------------------------------------- routes ------------------
@app.route('/')
def home():
    posts= Posts.query.order_by(- Posts.date_posted)[:3]
    return render_template('home.html',posts=posts)


@app.route('/user')
def user():
    user = current_user
    return render_template('user.html', user=user)


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
        flash("you now have an account congraitulation!")
    our_users = User.query.order_by(User.add_date)

    return render_template('add_user.html', form=form, name=name, our_users=our_users)

# update user info
@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update_user(id):
    form = Userform()
    user_to_update = User.query.get_or_404(id)
    if request.method == "POST":
        user_to_update.name = request.form['name']
        user_to_update.email = request.form['email']
        user_to_update.favourate_color = request.form['favourate_color']
        user_to_update.username = request.form['username']
        user_to_update.about_auther = request.form['about_auther']
        if request.files['profile_pic']:
            user_to_update.profile_pic = request.files['profile_pic']
            # git file name
            pic_filename = secure_filename(user_to_update.profile_pic.filename)
            pic_name = str(uuid.uuid1()) + "_" + pic_filename
            # save the image
            saver = request.files['profile_pic']
            saver.save(os.path.join(app.config['UPLOAD_FOLDER'],pic_name))
            # override the pic file to its name
            user_to_update.profile_pic = pic_name


            try:
                db.session.commit()
                flash("user updated successfuly")
                return render_template('update.html', form=form, user_to_update=user_to_update,id=id)
            except:
                flash("user updated error!! try again")
                return render_template('update.html', form=form, user_to_update=user_to_update,id=id)
        else:
            db.session.commit()
            flash("user updated successfuly")
            return render_template('update.html', form=form, user_to_update=user_to_update,id=id)
    else:
        return render_template('update.html', form=form, user_to_update=user_to_update,id=id)

# delete user
@app.route('/delete/<int:id>')
@login_required
def delete(id):
    name = None
    form = Userform()
    user_del = User.query.get_or_404(id)
    if id == current_user.id:
        try:
            db.session.delete(user_del)
            db.session.commit()
            flash("user deleted successfuly!")
            name = form.name.data
            our_users = User.query.order_by(User.add_date)
            return render_template('add_user.html', form=form, name=name, our_users=our_users)
        except:
            flash("oops something wrong!")
            return render_template('add_user.html', form=form, name=name, our_users=our_users)
    else:
        flash("oops something wrong! you can't delete that user permission denied")
        return redirect(url_for('add_user'))


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
        if user_to_check:
            passed = check_password_hash(user_to_check.password_hashed, password)

    return render_template('test_password.html', email=email, password=password, user_to_check=user_to_check, passed=passed, form=form)


# adding new post
@app.route('/add-post',methods=['GET','POST'])
def add_post():
    form = Postform()
    poster = current_user
    if form.validate_on_submit():
        post = Posts(title=form.title.data,content=form.content.data,poster_id=poster.id,slug=form.slug.data)
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
    posts = Posts.query.order_by(- Posts.date_posted)
    return render_template('posts.html',posts=posts)

#showing spacific post
@app.route('/posts/<int:id>')
def get_post(id):
    post = Posts.query.get_or_404(id)
    comments = Comments.query.filter_by(post_id=id)
    return render_template('onepost.html',post=post,comments=comments)


#edite spacific post
@app.route('/post/<int:id>',methods=['GET','POST'])
@login_required
def edit_post(id):
    form = Postform()
    post = Posts.query.get_or_404(id)
    user_id = current_user.id
    if request.method == "POST":
        post.title = request.form["title"]
        post.slug   = request.form["slug"]
        post.content= request.form["content"]
        if  request.files['post_pic']:
            post.post_pic = request.files['post_pic']
            # git file name
            pic_filename = secure_filename(post.post_pic.filename)
            pic_name = str(uuid.uuid1()) + "_" + pic_filename
            # save the image
            saver = request.files['post_pic']
            saver.save(os.path.join(app.config['UPLOAD_FOLDER'],pic_name))
            # override the pic file to its name
            post.post_pic = pic_name

            try:
                db.session.add(post)
                db.session.commit()
                flash("post updated successfuly")
                return redirect(url_for('get_post',id=post.id))
            except:
                flash("post updated error!! try again")
                return redirect(url_for('get_post',id=post.id))
        else:
            db.session.add(post)
            db.session.commit()
            flash("post updated successfuly")
            return redirect(url_for('get_post',id=post.id))


    if user_id == post.poster.id:
        form.title.data= post.title
        form.slug.data= post.slug
        form.content.data= post.content
        return render_template('edit_post.html',form=form,post=post)
    else:
        flash("you are not the autherized to edit that post")
        return redirect(url_for('posts'))



#delte spacific post
@app.route('/post/delete/<int:id>')
@login_required
def delete_post(id):
    post = Posts.query.get_or_404(id)
    user_del = current_user.id
    if user_del == post.poster.id:
        try:
            db.session.delete(post)
            db.session.commit()
            flash("the post deleted successfully")
            return redirect(url_for('posts'))
        except:
            flash("oops! some thing wronge during the deleting")
            return redirect(url_for('posts'))
    else:
        flash("you are not the autherized to delete that post")
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
    id = current_user.id
    user = User.query.get_or_404(id)
    return render_template('dashboard.html',user=user)


#logout
@app.route('/logout',methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    flash("you loged out we are welcome to see you again ")
    return redirect(url_for('login'))



@app.route('/search',methods=['POST'])
def search():
    form =Searchform()
    posts = Posts.query
    if form.validate_on_submit():
        search = form.searched.data
        posts = posts.filter(Posts.content.like('%' + search + '%'))
        posts = posts.order_by(Posts.title).all()
        return render_template('search.html',form=form,search=search,posts=posts)



@app.route('/admin')
@login_required
def admin():
    id = current_user.id
    if id == 1:
        
        return render_template('admin.html')
    else:
        flash("you must be an admin to access admin page")
        return redirect('dashboard')


# adding comment
@app.route('/add-comment/<int:id>',methods=['GET','POST'])
def add_comment(id):
    form = Commentform()
    commnter_id = current_user
    if form.validate_on_submit():
        comment = Comments(content=form.content.data,post_id=id,commnter_id=commnter_id.id)
        form.content.data=''


        db.session.add(comment)
        db.session.commit()
        flash("comment added successfuly")
        return redirect(url_for('get_post',id=id))
    return render_template("comment.html",form=form)


if __name__ == "__main__":
    app.run(debug=True)
