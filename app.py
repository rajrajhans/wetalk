from flask import Flask, g, render_template, redirect, flash, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import check_password_hash
import models
import forms

DEBUG = True
PORT = 8000

app = Flask(__name__)
app.secret_key='wshofj90792jwfjw903u2m093840298.!rajrajhans!'

login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view='login'

@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id==userid)
    except models.DoesNotExist:
        return None

@app.before_request
def before_request():
    #connect to the database
    g.db=models.DATABASE
    g.db.connect()
    g.user = current_user

@app.after_request
def after_request(response):
    #close database connection
    g.db.close()
    return response

@app.route('/register', methods=('GET', 'POST'))
def register():
    form=forms.RegisterForm()
    if form.validate_on_submit():
        flash('Registration successful', 'success')
        models.User.create_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        return redirect(url_for('index'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email==form.email.data)
        except models.DoesNotExist:
            flash("Email or password does not match", "error")
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("You have been logged in!", "success")
                return redirect(url_for('index'))
            else:
                flash("Email or password does not match", "error")
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", "success")
    return redirect(url_for('index'))

@app.route('/new_post', methods=('GET', 'POST'))
@login_required
def post():
    forme=forms.PostForm()
    if forme.validate_on_submit():
        models.Post.create(user=g.user._get_current_object(),
                           content=forme.content.data.strip())
        flash("Message Posted! Thanks", "success")
        return redirect(url_for('index'))
    return render_template('post.html', form=forme)
@app.route('/home')
def home():
    return render_template('homepage.html')
@app.route('/')
def index():
    stream= models.Post.select()
    return render_template('stream.html', stream=stream)

@app.route('/stream')
@app.route('/stream/<username>')
def stream(username=None, myprofile=None):
    template='stream.html'
    if myprofile==1:
        pass
    else:
        if username and username != current_user.username:
            user = models.User.select().where(models.User.username ** username).get()
            stream= user.posts
        else:
            stream = current_user.get_stream()
            user=current_user
    if username:
        template = 'user_stream.html'
        return render_template(template, stream=stream, user=user)

@app.route('/post/<int:post_id>')
def view_post(post_id):
    posts=models.Post.select().where(models.Post.id== post_id)
    return render_template('stream.html', stream=posts)

@app.route('/follow/<username>')
@login_required
def follow(username):
    try:
        to_user = models.User.get(models.User.username**username)
    except models.DoesNotExist:
        pass
    else:
        try:
            models.Relationship.create(
                from_user=g.user._get_current_object(),
                to_user=to_user
            )
        except models.IntegrityError:
            pass
        else:
            flash("You're now following {}!".format(to_user.username), "success")
    return redirect(url_for('stream', username=to_user.username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    try:
        to_user = models.User.get(models.User.username**username)
    except models.DoesNotExist:
        pass
    else:
        try:
            models.Relationship.get(
                from_user=g.user._get_current_object(),
                to_user=to_user
            ).delete_instance()
        except models.IntegrityError:
            pass
        else:
            flash("You've unfollowed {}!".format(to_user.username), "success")
    return redirect(url_for('stream', username=to_user.username))

if __name__=='__main__':
    models.initialize()
    try:

        models.User.create(
            username='Raj',
            email='raj@rajhans.com',
            password='password',
            is_admin=True
        )
    except:
        pass
    app.run(debug=DEBUG, port=PORT)