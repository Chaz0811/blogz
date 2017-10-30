from flask import Flask, request, redirect, render_template, send_file, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    blogtitle = db.Column(db.String(120))
    blogpost = db.Column(db.String(240))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, blogtitle, blogpost, owner):
        self.blogtitle = blogtitle
        self.blogpost = blogpost
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60))
    password = db.Column(db.String(30))
    blogs = db.relationship('Blog', backref='blogowner')

    def __init__(self, username, password):
        self.username= username
        self.password= password


@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'blog']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')        

@app.route('/', methods=['POST','GET'])
def index():
    blogposts = Blog.query.all()
    return render_template('blog.html', object_list=blogposts)

@app.route('/blog', methods=['POST', 'GET'])
def post():
    if request.method == 'POST':
                
        blogtitle_error = ''
        blogbody_error = ''
        blog_title = request.form['blogtitle']
        blog_body = request.form['blogpost']

        if blog_title == '':
            blogtitle_error = "Blog Title Cannot Be Blank"
        
        if blog_body == '':
            blogbody_error = "Blog Body Cannot Be Blank"
        
        if blogtitle_error != '' or blogbody_error != '':
            return render_template('newpost.html', blogtitle_error=blogtitle_error, blogbody_error=blogbody_error, title=blog_title, body=blog_body)
        else:
            new_blog = Blog(blog_title,blog_body)
            db.session.add(new_blog)
            db.session.commit()  
            return redirect('/blog?id=' + str(new_blog.id))
            

        
    
    
    if request.method =='GET':
        post_id = request.args.get('id')
        this_post = Blog.query.get(int(post_id))
        title = this_post.blogtitle
        entry = this_post.blogpost
        return render_template('blog_post.html',post_title=title,post_body=entry)

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    return render_template('newpost.html')

@app.route('/signup', methods=['POST', 'GET'])
def sign_up():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()

        user_error = ''
        password_error = ''
        verify_error = ''
        
        if username == '':
            username_error = 'Please enter Username'
        elif len(username) < 3:
            username_error = 'Username must contain at least 3 characters'
        elif username == existing_user:
            username_error = 'Username already in use'

        if password == '':
            password_error = 'Please enter a password'
        elif len(password) < 3:
            password_error = 'Password must contain at 3 characters'
        elif password != verify:
            password_error = 'Passwords do not match'
            verify_error = 'Passwords do not match'
        
        if verify == '':
            verify_error = 'Double check your password'
        
        
        
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')

    return render_template('signup.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        username_error = ''
        password_error = ''

        if user and user.password == password:
            session['username'] = username          
            return redirect('/newpost')
        elif user and user.password != password:
            password_error = 'Password is incorrect, please try again'
        elif user and user.username != username:
            username_error = 'Username is incorrect or you do not have an account'
        return render_template('login.html', username=username, username_error=username_error, password_error=password_error)
    
    return render_template('login.html')

@app.route('/index', methods=['POST', 'GET'])
def blogger_list():
    user_list = User.query.all()
    return render_template('index.html', user_list= user_list)

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')


if __name__ == '__main__':
    app.run()