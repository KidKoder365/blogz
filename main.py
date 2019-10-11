from flask import Flask, request, redirect, render_template, session,flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:root@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True  #helps debug by giving information in the terminal
db = SQLAlchemy(app)
app.secret_key = 'secretBLOGZ'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120)) #title of blog title
    blog = db.Column(db.String(256)) #blog post
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, blog, owner):
        self.title = title
        self.blog = blog
        self.owner = owner

class User(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True) #username with unique = True so there is no duplicate
    password = db.Column(db.String(256)) #password
    blogs = db.relationship('Blog', backref = 'owner') # relationship between blog table and this user

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'blog','signup', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/', methods=['POST', 'GET'])
def index():

    users = User.query.all() #show all users on homepage
    return render_template('/index.html', users = users, title="Blogz")

@app.route('/signup', methods = ['POST','GET'])
def signup():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        for i in username:
            if i == " ":
                error = "Username should not have any spaces."
                return render_template("signup.html",error=error, username=username)

        for i in password:
            if i == " ":
                error = "Password should not have any spaces."
                return render_template("signup.html",error1=error, username=username)

    
        if len(username) < 3 or len(username) > 20:
            error = "Entry is not valid.  Username needs to be between 3-20 character long"
            return render_template("signup.html",error=error, username=username)

        elif len(password) < 3 or len(password) > 20:
            error = "Password entry is not valid.  Password needs to be between 3-20 character long."
            return render_template("signup.html",error1=error, username=username)

        elif len(verify) < 3:
            error = "Password does not match.  Entry does not seem to be long enough."
            return render_template("signup.html",error2=error, username=username)

        elif password != verify:
            error = "Password does not match.  Please confirm they are the same in both fields."
            return render_template("signup.html",error2=error, username=username)


        else:       #after passing above conditions, user info is saved to database and is sent to /newpost
            if request.method == 'POST':
                username = request.form['username']
                password = request.form['password']
                verify = request.form['verify']
            
                new_user = User(username,password)
            
                db.session.add(new_user)
                db.session.commit()
                # "remember" that the user has logged in
                session['username'] = username
                flash("Logged in as " + username)
        
            
            return redirect("/newpost")
    return render_template('/signup.html')

@app.route('/login', methods = ['POST', 'GET'])
def login():

    #correct password and redirected to /newpost with username stored in a session
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            # "remember" that the user has logged in
            session['username'] = username
            flash("You're login as " + username)
        

            return redirect('/newpost')

        #user enter username stored in datablase with an incorrect password and is redirected to /login with error message
        elif user and user.password != password: 
            # TODO - explain why login fail
            flash("User password incorrect", 'error')
            return redirect('/login')

        else: #else username does not exist
            flash("Username does not exist")
            return redirect('/login')
    
    return render_template('/login.html')


@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')



@app.route('/blog', methods = ['POST', 'GET'])
def blog():

    user_id = request.args.get('userid')
    blog_id = request.args.get('id')


    #if there is an user_id (Author), then return blog posts by that Author
    if user_id != None:
        blogsByAuthor = Blog.query.filter_by(owner_id=user_id).all() #filter all Blogs by Author
        return render_template('/singleUser.html', blogsByAuthor = blogsByAuthor)

    #if there is blog_id(blog entry), then render page to just show that entry
    elif blog_id != None:
        task = Blog.query.get(blog_id) # if there is an id, return just the blog pertaining to id
        user = Blog.query.filter_by(id=blog_id).first()
        return render_template('/blog_entry.html', task = task, username = user.owner.username, title = "Blog Entry")

    #if no blog_id and no user_id, then show all blogs
    tasks = Blog.query.all()

    return render_template('/blog.html', tasks=tasks, title ="Blogz")

@app.route('/newpost', methods = ['POST','GET'])
def new_post():
    blog_title=""
    blog=""
    
    if request.method == 'POST':
        blog_title=request.form['blog-title']
        blog = request.form['blog']
        owner = User.query.filter_by(username=session['username']).first() #get username from User Table using session and directing to /newpost

        if len(blog_title) == 0 and len(blog) == 0:
            error = "Please fill in the title."
            error1 = "Please fill in the body."
            return render_template('/newpost.html', blog_title=blog_title, blog=blog, error = error, error1 = error1)

        elif len(blog_title) == 0:
            error = "Please fill in the title."
            return render_template('/newpost.html', blog_title=blog_title, blog=blog, error = error)

        elif len(blog) == 0:
            error = "Please fill in the body."
            return render_template('/newpost.html', blog_title=blog_title, blog=blog, error1 = error)
        else:

            new_blog = Blog(blog_title, blog, owner)
            db.session.add(new_blog)
            db.session.commit()

            blog_id = new_blog.id
           

            return redirect('/blog?id={0}'.format(blog_id)) #, username=owner, task=new_blog, title="New Entry")


    return render_template('/newpost.html', blog_title=blog_title, blog=blog , title="New Entry")

if __name__== '__main__':
    app.run()