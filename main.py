import os
from uuid import uuid4
import pickle

from flask import Flask, request, session, render_template, redirect, flash, url_for
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from flask_caching import Cache

from models import db, User, Post
from forms import SignIn, SignUp, PostForm


load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_URI')
app.config["CACHE_TYPE"] = 'SimpleCache'
app.config["CACHE_DEFAULT_TIMEOUT"] = 10
app.secret_key = os.getenv('SECRET_KEY')

app.logger.setLevel("INFO")

db.init_app(app)
login_manager = LoginManager()
login_manager.login_message = "You must be logged in to access this page."
login_manager.login_view = 'sign_in'
login_manager.init_app(app)
csrf_protect = CSRFProtect(app)
cache = Cache(app)

# with app.app_context():
#     db.drop_all()
#     db.create_all()

# @login_manager.user_loader
# def get_current_user(id: int):
#     user = cache.get(id)
#     if user:
#         user = pickle.loads(user)
#     else:
#         user = User.query.filter_by(id=id).first()
#         cache.set(id, pickle.dumps(user))
#         print("Requested database request")

#     return user

@login_manager.user_loader
@cache.cached(timeout=15)
def get_current_user(id: int):
    print("Asking for database")
    app.logger.info("Asking for database")
    return User.query.filter_by(id=id).first()



@app.route('/sign-up/', methods= ['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form.get('username')
        user = User.query.filter_by(username=username).first()
        if user:
            flash(f"User with username {username} already exists")
            app.logger.warning(f"User with username {username} already exists")
            return redirect(url_for('sign_up'))
        
        user = User(
            username=username,
            first_name=request.form.get('first_name') or None,
            last_name=request.form.get('last_name') or None,
            password=request.form.get('password')
        )

        db.session.add(user)
        db.session.commit()
        flash("You have successfully registered")
        app.logger.info(f"User with username {username} has been successfully registered")
        return redirect(url_for('sign_in'))
    
    app.logger.info("Rendering sign up page")
    return render_template('sign_up.html')


@app.route('/sign-in/', methods= ['GET', 'POST'])
def sign_in():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        print(user, user.is_verify_password(password) if user else None, user.is_active if user else None)
        if not any ([user, user.is_verify_password(password), user.is_active]):
            flash("Invalid username or password")
            app.logger.error("Someone hacking our system...")
            return redirect(url_for('sign_in'))
        
        login_user(user)
        app.logger.info("USER LOGGED IN!!!")
        return redirect(url_for('index'))
    return render_template('sign_in.html')


@login_required
@app.get('/logout/')
def logout():
    flash("You have successfully logged out")
    logout_user()
    return redirect(url_for('sign_in'))
        
@app.route('/add-post/', methods=['GET', 'POST'])
@login_required
def add_post():
    if request.method == 'POST':
        image = request.files.get('image')
        if not image and not image.filename:
            image = None
        else:
            image_name = secure_filename(image.filename)
            if not image_name:
                image = None
            else:
                image_name = uuid4().hex + "_" + image_name
                image.save("static/" + image_name)
                image = image_name
        
        post = Post(
            title=request.form.get('title'),
            text=request.form.get('text'),
            user=current_user,
            image=image

        )
        db.session.add(post)
        db.session.commit()
        flash("You have successfully added a post")
        return redirect(url_for('index'))
    return render_template('add_post.html')


@app.route('/sign-up-form/', methods = ['GET', 'POST'])
def sign_up_form():
    form = SignUp()
    if form.validate_on_submit():
        user = User(
            username = form.username.data,
            first_name = form.first_name.data or None,
            last_name = form.last_name.data or None,
            password = form.password.data
        )
        db.session.add(user)
        db.session.commit()
        flash("You have successfully registered")
        return redirect(url_for('sign_in_form'))
    return render_template('sign_up_form.html', form=form)


@app.route('/sign-in-form/')
def sign_in_form():
    form = SignIn()
    if form.validate_on_submit():
        user: User = User.query.filter_by(username=form.username.data).first()
        if user and user.is_verify_password(form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        flash("Invalid username or password")
    return render_template('sign_in_form.html', form=form)


@app.route('/add-post-form/', methods=['GET', 'POST'])
def add_post_form():
    form = PostForm()
    if form.validate_on_sumbit():
        post = Post(
            title=form.title.data,
            text=form.text.data,
            image=None
        )
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_post_form.html', form=form)

@app.get('/')
def index():
    posts = Post.query.all()
    return render_template("index.html", posts=posts)



if __name__ == '__main__':
    app.run(debug=True)



        