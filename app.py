from flask import Flask, render_template, redirect, request, flash, session, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///DB_FILE.db'
db = SQLAlchemy(app)
app.secret_key = "hello"
app.permanent_session_lifetime = timedelta(minutes=5)

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(20), nullable=False, default="N/A")
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return 'Blog post' + str(self.id)


class User(db.Model):
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    id = db.Column(db.Integer, primary_key=True)

    def __init__(self, _email, _password, _id=0):
        self.email = _email
        self.password = _password
        self.id = _id

    def __repr__(self):
        return 'user name: '+ self.user_name + 'password'+ self.password


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/posts', methods=['POST', 'GET'])
def posts():
    if request.method == 'POST':
        post_title = request.form['title']
        post_content = request.form['content']
        post_author = request.form['author']
        new_post = BlogPost(title=post_title, content=post_content, author=post_author,id=session["id"])
        db.session.add(new_post)
        db.session.commit()
        return redirect('/posts')
    else:
        all_posts = BlogPost.query.filter_by(id=session["id"]).order_by(BlogPost.date_posted).all()
        return render_template("posts.html", posts=all_posts)


@app.route('/posts/delete/<int:id>')
def delete(id):
    post = BlogPost.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    return redirect('/posts')


@app.route('/posts/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if "id" in session:
            return redirect(url_for("posts"))
        return render_template('login.html')
    user = User(request.form['inputEmail'], request.form['inputPassword'])
    users = User.query.all()
    res = User.query.filter_by(password=user.password).first()
    if res != None:
        session.permanent = True
        session["id"] = user.id
        posts = BlogPost.query.filter_by(id=session["id"])
        if len(posts) > 0:
            return render_template('posts.html', posts=posts)
        return redirect('/posts')
    error = 'You are not logged in before...'
    return render_template('login.html', message=error, error=error) 

@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    post = BlogPost.query.get_or_404(id)
    if request.method == 'POST':
        post.title = request.form['title']
        post.author = request.form['author']
        post.content = request.form['content']
        db.session.commit()
        return redirect('/posts')
    else:
        return render_template('edit.html', post=post)

@app.route('/posts/new', methods=['GET', 'POST'])
def new():
    print("new")
    return render_template('new_file.html')

@app.route('/posts/signUp', methods=['GET', 'POST'])
def sign_up():
    print(request.method)
    if request.method == 'POST':
        user = User(request.form['email'], request.form['password'])
        users = User.query.all()
        res = False
        print('dame')
        user_res = 0
        for x in users:
            if x.id == user.id:
                res = True 
        if not(res):
            print('hey')
            db.session.add(user)
            db.session.commit()
            return render_template('posts.html', [])
        else:
            session["id"] = user.id
            posts = BlogPost.query.filter_by(id=user.id)
            return render_template('posts.html', posts=posts)
    else:
        print('printing something')
        return render_template('signUp.html')

if __name__ == "__main__":
    app.run(debug=True)
