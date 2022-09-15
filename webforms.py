from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, validators, PasswordField, BooleanField, ValidationError,TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField
from flask_wtf.file import FileField


class Loginform(FlaskForm):
    username= StringField("username",validators=[DataRequired()]) 
    password= PasswordField("password",validators=[DataRequired()]) 
    submit = SubmitField("submit")






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
    about_auther = TextAreaField("about auther")
    password_hashed = PasswordField("password", validators=[DataRequired(
    ), EqualTo('password_hashed2', message='password must match!')])
    password_hashed2 = PasswordField(
        "confirm the password", validators=[DataRequired()])
    profile_pic = FileField("profile pic")
    submit = SubmitField("submit")




class Postform(FlaskForm):
    title     = StringField("title",validators=[DataRequired()])
    # content = StringField("content",validators=[DataRequired()],widget=TextArea())
    content   = CKEditorField("content",validators=[DataRequired()])
    auther    = StringField("auther")
    slug      = StringField("slug",validators=[DataRequired()])
    post_pic  = FileField("post pic")
    submit    = SubmitField("submit")



class Searchform(FlaskForm):
    searched = StringField("search",validators=[DataRequired()])
    submit   = SubmitField("submit")