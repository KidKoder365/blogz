from flask import Flask, request, redirect, render_template, session,flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:root@localhost:3306/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True  #helps debug by giving information in the terminal
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120)) #name of blog title
    blog = db.Column(db.String(256)) #blog post

    def __init__(self, name, blog):
        self.name = name
        self.blog = blog

@app.route('/', methods=['POST', 'GET'])
def index():

    tasks = Blog.query.all() #show all blogs on homepage
    return render_template('/blog.html', tasks = tasks, title="Build-A-Blog")

@app.route('/blog', methods = ['POST', 'GET'])
def blog():

    blog_id = request.args.get('id')

    if blog_id == None:  # if no id in Get Method, return all tasks
        tasks = Blog.query.all()
        return render_template('/blog.html', tasks = tasks, title = "Build-a-Blog")

    else:
        task = Blog.query.get(blog_id) # if there is an id, return just the blog pertaining to id
        return render_template('/blog_entry.html', task = task, title = "Blog Entry")

@app.route('/newpost', methods = ['POST','GET'])
def new_post():
    task=""

    if request.method == 'POST':
        blog_title=request.form['blog-title']
        blog = request.form['blog']

        if len(blog_title) == 0 and len(blog) == 0:
            error = "Please fill in the title."
            error1 = "Please fill in the body."
            return render_template('/newpost.html', task=task, error = error, error1 = error1)

        elif len(blog_title) == 0:
            error = "Please fill in the title."
            return render_template('/newpost.html', task=task, error = error)

        elif len(blog) == 0:
            error = "Please fill in the body."
            return render_template('/newpost.html', task=task, error1 = error)
        else:

            new_blog = Blog(blog_title, blog)
            db.session.add(new_blog)
            db.session.commit()
            

            return render_template('blog_entry.html', task=new_blog, title="New Entry")

    return render_template('/newpost.html', task=task , title="New Entry")

if __name__== '__main__':
    app.run()