from flask import Flask, request, redirect, render_template, send_file, session, flash
from hash import make_pw_hash, check_pw_hash
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
    pw_hash = db.Column(db.String(30))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username= username
        self.pw_hash= make_pw_hash(password)


@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'blog']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')        

@app.route('/', methods=['POST', 'GET'])
def index():
    userlist =  User.query.all()
    return render_template('index.html',userlist=userlist)

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    
    if request.args.get('id'):
       
        blog = Blog.query.filter_by(id=request.args.get('id')).first()
        user = User.query.filter_by(id=blog.owner_id).first()
        title = blog.blogtitle
        body = blog.blogpost
        return render_template('blog_post.html',post_title=title,post_body=body, user=user)
    
    elif request.args.get('user'):
       
        user = User.query.filter_by(id=request.args.get('user')).first()
        blogs = Blog.query.filter_by(owner_id=request.args.get('user'))
        return render_template('singleUser.html', blogs=blogs, user=user)
          
    else:
        blog_posts = Blog.query.all()
        users = User.query.all()
        return render_template('blog.html', blog_posts=blog_posts, users=users)        

        
    
    
    if request.method =='GET':
        post_id = request.args.get('id')
        this_post = Blog.query.get(int(post_id))
        title = this_post.blogtitle
        entry = this_post.blogpost
        return render_template('blog_post.html',post_title=title,post_body=entry)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':

        title_error = ''
        body_error = '' 
        blog_title = request.form['blogtitle']
        blog_body = request.form['blogpost'] 

        if blog_title == '':
            title_error = 'This blog needs a title!'
        if blog_body == '':
            body_error = 'This blog needs some sustenance!'

        if title_error != '' or body_error != '':
            return render_template('newpost.html', title_error=title_error, body_error=body_error, title=blog_title, body=blog_body)
        else:   
            new_blog = Blog(blog_title,blog_body,owner)
            db.session.add(new_blog)
            db.session.commit()  
            return redirect('/blog?id=' + str(new_blog.id))

    return render_template('newpost.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
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
            return redirect('/')

    return render_template('signup.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        username_error = ''
        password_error = ''

        if user and check_pw_hash(password, user.pw_hash):
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
    return redirect('/')


if __name__ == '__main__':
    app.run()