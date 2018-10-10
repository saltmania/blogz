from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:1234bab@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))

    def __init__(self, title, body):
        self.title = title
        self.body = body
        
@app.route('/newpost')
def new_post():
    return render_template('newpost.html',title="Add a Blog Entry!")

@app.route('/newpost', methods=['POST'])
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

#
#  Add database post  stuff here I guess
#  Form redirect String as GET
# is this (database commit) in the wrong spot? ... but how else to get ID and send that as param

   if (title_error=='' and body_error==''):
       new_blog = Blog(new_title, new_body)
       db.session.add(new_blog)
       db.session.commit()
       new_id= new_blog.id
       new_blog_link="/blog?id="+str(new_id)
       return redirect(new_blog_link)

   return redirect('/blog')



@app.route('/blog', methods=['POST', 'GET'])
def showBlog():

    if request.method=='POST':
        blogs = Blog.query.all()

        return render_template('displayBlogs.html',
            title="Build A Blog",
            blogs=blogs)

    if 'id' in request.args:
        new_blog_id = request.args.get('id')
        new_blog= Blog.query.filter_by(id=new_blog_id).all()
        
        return render_template('displayBlogs.html',
            title="Build a Blog",
            blogs=new_blog
            )
    else:
        blogs = Blog.query.all()
        return render_template('displayBlogs.html',title="Build A Blog", 
            blogs=blogs)

    return "<h1>We're not home right now</h1>"

    

@app.route('/')
def index():
    return redirect('/blog')


if __name__ == '__main__':
    app.run()