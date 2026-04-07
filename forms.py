from flask_wtf import FlaskForm
import wtforms


class SignUp(FlaskForm):
    username = wtforms.StringField(
        label = 'Input login',
        validators=[wtforms.validators.DataRequired(), wtforms.validators.Length(min=3, max=1000)]
        )
    first_name = wtforms.StringField(label='First Name')
    last_name = wtforms.StringField(label='Last Name')
    password = wtforms.PasswordField(
        label='Password', 
        validators=[wtforms.validators.DataRequired(), wtforms.validators.Length(min=6)])
    
    submit = wtforms.SubmitField(label='Sign Up')

class SignIn(FlaskForm):
    username = wtforms.StringField(label='Login', validators=[wtforms.validators.DataRequired()])
    password = wtforms.PasswordField(label='Password', validators=[wtforms.validators.DataRequired()])
    submit = wtforms.SubmitField(label='Sign In')


class PostForm(FlaskForm):
    title = wtforms.StringField(
        label='Title', 
        validators=[wtforms.validators.DataRequired(), wtforms.validators.Length(min=3, max=1000)])
    text = wtforms.TextAreaField(
        label='Text', 
        validators=[wtforms.validators.DataRequired(), wtforms.validators.Length(min=3, max=1000)])
    image = wtforms.FileField(label='Image')
    submit = wtforms.SubmitField(label='Add Post')