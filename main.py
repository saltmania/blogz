from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy

import cgi
import os

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz1234@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

app.secret_key='LaunchCode101'


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    email = db.Column(db.String(120))
    
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

class Blog(db.Model):
        
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))

    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    owner_name = db.Column(db.String(120))

    def __init__(self, title, body, owner_id, owner_name):
        self.title = title
        self.body = body
        self.owner_id = owner_id
        self.owner_name=owner_name

#############################################
# Begin Route Handlers for building a new Blog Post at /newpost

@app.route('/blog/newpost')
def newpost():
    return render_template('newpost.html',title="Blogz")


@app.route('/blog/newpost', methods=['POST'])
def validate_blog():
   new_title=request.form['title']
   new_body=request.form['body']

   title_error=''
   body_error=''

   if new_title=='':
       title_error="Please fill in the title"
   if new_body=='':
       body_error="Please fill in the body"

   if (title_error!='' or body_error!=''):
       return render_template('newpost.html',
       title="Build A Blog",
       title_error=title_error,
       body_error=body_error)


   if (title_error=='' and body_error==''):
       owner= User.query.filter_by(username=session['username']).first()
       owner_id=owner.id
       owner_name=owner.username
       new_blog = Blog(new_title, new_body, owner_id, owner_name)
       db.session.add(new_blog)
       db.session.commit()
       new_id= new_blog.id
       new_blog_link="/blog?id="+str(new_id)
       return redirect(new_blog_link)

   current_user= User.query.filter_by(username=session['username']).first()

   return redirect('/blog?user={0}'.format(current_user.username))

# END Route Handlers for building a new Blog Post
#############################################

#############################################
# Begin Route Handlers for Display of Blogs at /blog

@app.route('/blog', methods=['POST', 'GET'])
def showBlog():

    if request.method=='POST':
        blogs = Blog.query.all()

        return render_template('displayBlogs.html',
            title="Build A Blog",
            blogs=blogs)

    if 'id' in request.args:                        ##### If Blog ID is in the args, display the single blog
        new_blog_id = request.args.get('id')
        new_blog= Blog.query.filter_by(id=new_blog_id).all()
        
        return render_template('displayBlogs.html',
            title="Blogz",
            blogs=new_blog
            )
    elif 'user' in request.args:                    ##### if User in Args then display blogs based on user
        blog_user = request.args.get('user')
        user_id = User.query.filter_by(username=blog_user).first().id
     
        new_blog= Blog.query.filter_by(owner_id=user_id).all()
        return render_template('displayBlogs.html',
            title="Build a Blog",
            blogs=new_blog
            )

    else:
        blogs = Blog.query.all()
        return render_template('displayBlogs.html',title="Build A Blog", 
            blogs=blogs)

    return "<h1>We're not home right now</h1>"


# END Route Handlers for Display of Blogs at /blog
#############################################

######## IMPORTED CODE BEGIN #################
@app.route("/signup")
def signup():
    
    return render_template('signup_template.html')

 #Begin Validate User Login Signup block   

@app.route('/signup', methods=['POST'])
def signupValidate():
   username=request.form['username']
   password=request.form['password']
   v_password=request.form['verify']
   user_email=request.form['email']


   #### TODO add some more user validation and error checking when attempting to sign in like "Username Taken"

   username_error= ''
   password_error= ''
   v_error=''
   email_error=''

   space = ' '
   blank = ''
   min_len=3
   max_len=20

   #check if Username, PW, or Verify PW have been left blank
   if (username==''):
       username_error = "Dont leave blank"
   if (password==''):
       password_error = "Dont leave blank" 
   if (v_password==''):
       v_error = "Dont leave blank" 

    #Verify Username Characters
   if (username!=blank):
      if space in username:
         username_error="I said no spaces!"
      if ((len(username)<min_len) | (len(username)>max_len)):
         username_error= "Please use a User Name between 3 and 20 characters"

    #Verify Username not already in DB
   if User.query.filter_by(username=username).all():
       username_error="Username already exhists.  Please use a different name"

   #check if passwords match
   if (password!=v_password):
      password_error = "Passwords do not match"
      v_error="Passwords do not match"
   if ((len(password)<min_len) | (len(password)>max_len)):
         password_error= "Please use a Password between 3 and 20 characters"

    #Verify Email Characters
   if (user_email!=blank):
      if space in user_email:
         email_error="I said no spaces!"
      if '@' not in user_email:
         email_error = "Valid emails have an @ symbol"
      if '.' not in user_email:
         email_error= "Valid emails have a . in them"
      if (len(user_email)<min_len) | (len(user_email)>max_len):
         email_error= "Please use an Email between 3 and 20 characters"



   #Place holder code if User gets all requirements right ...Redirect to Welcome Area
   if((username_error==blank) and (password_error==blank) and (v_error==blank) and (email_error==blank)):
         new_User = User(username, password)
         new_User.email=user_email
         db.session.add(new_User)
         db.session.commit()
         
         session['username'] = new_User.username
         return redirect('/blog/newpost')
    
   else:
      return render_template('signup_template.html',
         name=username,
         email=user_email,
         username_error=username_error,
         password_error=password_error,
         verify_error=v_error,
         email_error=email_error)



######## IMPORTED CODE END #################

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def loginValidate():



    userAttempted = request.form['username']
    pwAttempted = request.form['password']

    validateUser = User.query.filter_by(username=userAttempted).first()


    ###TODO Add all the fun validation and checking
    if not validateUser:
        return render_template('login.html', 
            username_error = "User Name not found")

    if validateUser and ( not validateUser.password==pwAttempted):
        return render_template('login.html', 
            password_error = "Password not correct")


    if validateUser and validateUser.password==pwAttempted:
        session['username'] = validateUser.username
        return redirect('/blog/newpost')

    ##### Add Session Stuff
    return "<h1>Other Login Error, please come again</h1>"

@app.route('/logout')
def logout():

    if 'username' in session:
        del session['username']

    return redirect('/blog')


#############################################
# Begin Route Handlers for Root at /

@app.before_request
def require_login():
    allowed_routes = ['index','login', 'loginValidate', 'signupValidate', 'signup','showBlog','logout']
    if (request.endpoint not in allowed_routes) and ('username' not in session):
        return redirect('/login')


@app.route('/')
def index():

    users = User.query.all()

    return render_template('displayUsers.html',
        title="Blogz",
        users=users)


if __name__ == '__main__':
    app.run()