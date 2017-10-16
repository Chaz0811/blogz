from flask import Flask, request, redirect, render_template, send_file
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    blogtitle = db.Column(db.String(120))
    blogpost = db.Column(db.String(240))

    def __init__(self, blogtitle, blogpost):
        self.blogtitle = blogtitle
        self.blogpost = blogpost
        

@app.route('/', methods=['POST','GET'])
def index():
    blogposts = Blog.query.all()
    return render_template('blog.html', object_list=blogposts)

@app.route('/blog', methods=['POST', 'GET'])
def post():
    if request.method == 'POST':
        blog_title = request.form['blogtitle']
        blog_body = request.form['blogpost']
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
    return render_template('newpost.html', title='Build-A-Blog!')



if __name__ == '__main__':
    app.run()