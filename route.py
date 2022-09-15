from flask import Flask, request, jsonify, render_template, flash,redirect,url_for
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
from flask_login import UserMixin , login_user , LoginManager , login_required , logout_user,current_user
from webforms import Loginform,Nameform,Passwordform,Postform,Userform,Searchform
from werkzeug.utils import secure_filename
import uuid as uuid
import os
from models import User,Posts
import app



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
    user_id = current_user.id
    if form.validate_on_submit():
        post.title = form.title.data
        post.slug   = form.slug.data
        post.content= form.content.data
        db.session.add(post)
        db.session.commit()
        flash("post has been updated successfuly")
        return redirect(url_for('get_post',id=post.id))
    if user_id == post.poster.id:
        form.title.data= post.title
        form.slug.data= post.slug
        form.content.data= post.content
        return render_template('edit_post.html',form=form)
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
