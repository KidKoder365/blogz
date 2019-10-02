from flask import Flask, request, redirect, render_template, session,flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:root@localhost:3306/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True  #helps debug by giving information in the terminal
db = SQLAlchemy(app)
app.secret_key = "launchcode"


class Task(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120)) #name of blog title
    blog = db.Column(db.String(256)) #blog post
    completed = db.Column(db.Boolean)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, name, blog, owner):
        self.name = name
        self.blog = blog
        self.completed = False
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    tasks = db.relationship('Task', backref='owner')

    def __init__(self,email, password):
        self.email = email
        self.password = password

@app.before_request
def required_login():
    allowed_routes = ['login', 'register']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')


@app.route('/login', methods=['POST','GET'])
def login():

    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            # "remember" that the user has logged in
            session['email'] = email
            flash("Logged in")
        

            return redirect('/')

        else:
            # TODO - explain why login fail
            flash("User password incorrect, or user does not exist", 'error')
            return render_template('login.html')
            



    return render_template('login.html')

@app.route('/logout')
def logout():
    del session['email']
    return redirect('/')

@app.route('/register',methods=['POST','GET'])
def register():

    if request.method == 'POST':
        email=request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        #TODO - validate user's data

        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()

            # 'remember' the user
            session['email'] = email
            return redirect('/login')

        else:
            # TODO - user better respnse messaging
            return 'Duplicate user'

    return render_template('register.html')


@app.route('/', methods=['POST', 'GET'])
def index():

    owner = User.query.filter_by(email =session['email']).first()
    if request.method == 'POST':
        task_name = request.form['task']
        
        new_task = Task(task_name, owner)
        db.session.add(new_task)
        db.session.commit()

    tasks = Task.query.filter_by(completed=False, owner=owner).all()
    completed_tasks=Task.query.filter_by(completed=True, owner = owner).all()
   

    return render_template('/todos.html', title="Build A Blog",
        tasks=tasks, completed_tasks=completed_tasks)

@app.route('/blog', methods = ['POST', 'GET'])
def blog():
    owner = User.query.filter_by(email =session['email']).first()
    if request.method == 'POST':
        blog_title=request.form['blog-title']
        blog = request.form['blog']
        new_blog = Task(blog_title, blog, owner)
        db.session.add(new_blog)
        db.session.commit()

    tasks = Task.query.filter_by(completed=False, owner=owner).all()
    completed_tasks=Task.query.filter_by(completed=True, owner = owner).all()
    return render_template('blog.html', tasks = tasks, completed_tasks = completed_tasks)

@app.route('/blogpost', methods = ['POST', 'GET'])
def blogpost():

    owner = User.query.filter_by(email =session['email']).first()
    tasks = Task.query.filter_by(completed=False, owner=owner).all()

    task_id = int(request.form['task-id'])
    task = Task.query.get(task_id)
    db.session.add(task)
    db.session.commit()
    blog_title = request.args.get('task.name')
    blog = request.args.get('task.blog')
    return render_template("base.html", blog_title=blog_title, blog=blog)

@app.route('/newpost', methods = ['POST','GET'])
def new_post():
    owner = User.query.filter_by(email =session['email']).first()
    tasks = Task.query.filter_by(completed=False, owner=owner).all()
    completed_tasks=Task.query.filter_by(completed=True, owner = owner).all()
    if request.method == 'POST':
        blog_title=request.form['blog-title']
        blog = request.form['blog']

        if len(blog_title) == 0 and len(blog) == 0:
            error = "Please fill in the title."
            error1 = "Please fill in the body."
            return render_template('/newpost.html', error = error, error1 = error1)



        elif len(blog_title) == 0:
            error = "Please fill in the title."
            return render_template('/newpost.html', error = error)

        elif len(blog) == 0:
            error = "Please fill in the body."
            return render_template('/newpost.html', error1 = error)      
        new_blog = Task(blog_title, blog, owner)
        db.session.add(new_blog)
        db.session.commit()

        tasks = Task.query.filter_by(completed=False, owner=owner).all()
        return render_template('/blog.html', title="Build a Blog",
        tasks=tasks, completed_tasks=completed_tasks)


   

    return render_template('/newpost.html', title="Build a Blog",
        tasks=tasks, completed_tasks=completed_tasks)

@app.route('/add-blog', methods = ['POST'])
def add_blog():

    owner = User.query.filter_by(email =session['email']).first()
    if request.method == 'POST':
        blog_title=request.form['blog-title']
        blog = request.form['blog']
        new_blog = Task(blog_title, blog, owner)
        db.session.add(new_blog)
        db.session.commit()

    tasks = Task.query.filter_by(completed=False, owner=owner).all()
    completed_tasks=Task.query.filter_by(completed=True, owner = owner).all()
   

    return render_template('/todos.html', title="Build a Blog",
        tasks=tasks, completed_tasks=completed_tasks)

@app.route('/delete-task', methods=['POST'])
def delete_task():
    task_id = int(request.form['task-id'])
    task = Task.query.get(task_id)
    task.completed = True
    db.session.add(task)
    db.session.commit()

    # db.session.delete(task)
    # db.session.commit()

    return redirect('/')

if __name__== '__main__':
    app.run()