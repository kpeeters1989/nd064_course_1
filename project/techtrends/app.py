import sqlite3
import datetime
import logging 

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

def get_now():
     date_now = (datetime.datetime.now())
     return date_now

def get_formatted_time():
    return datetime.datetime.strftime( get_now(), '%d/%m/%Y, %H:%M:%S')

conn_count=0

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global conn_count
   
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    conn_count=conn_count+1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    app.logger.debug('Get Post ID '+ str(post_id))
    return post

def get_nbr_post():
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return len(post)

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)


@app.route('/healthz')
def healthz():
    response = app.response_class(
           response=json.dumps({"result": "OK - healthy"}),
            status=200,
            mimetype='application/json'
    )
    app.logger.info('healthz request successfull')
    #print('healthz request successfull')
    return response


@app.route('/metrics')
def metrics():
    response = app.response_class(
           response=json.dumps({"status":"success","code":0,"data":{"db_connection_count": conn_count, "post_count": get_nbr_post()}}),
            status=200,
            mimetype='application/json'
    )
    app.logger.info('Metric request successfull')
    #print('Metric request successfull')
    return response



# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      app.logger.debug('%s , Article ID  %s does not exist!',get_formatted_time(),post_id) 
      #print("%s , Article ID  %s does not exist!" % (get_formatted_time(),post_id))
      return render_template('404.html'), 404
    else:
      app.logger.debug('%s , Article %s retrieved!',get_formatted_time(),post[2])
      #print("%s , Article %s retrieved!" % (get_formatted_time(),post[2]))
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.debug('%s , "About Us" page is retrieved!',get_formatted_time())
    #print("%s , \"About Us\" page is retrieved!" % get_formatted_time())
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            app.logger.debug('%s , Article %s created!',get_formatted_time(),title)
            #print("%s , Article %s created!" % (get_formatted_time(),title))
            return redirect(url_for('index'))

    return render_template('create.html')

# start the application on port 3111
if __name__ == "__main__":
     # set logger to handle STDOUT and STDERR 
    stdout_handler =  logging.StreamHandler(sys.stdout)
    stderr_handler =  logging.StreamHandler(sys.stderr)
    handlers = [stderr_handler, stdout_handler]
    
    logging.basicConfig(level=logging.DEBUG,format='%(levelname)s:%(name)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S',handlers=handlers)
    logging.basicConfig(level=logging.INFO,format='%(levelname)s:%(name)s %(message)s',  datefmt='%Y-%m-%d %H:%M:%S',handlers=handlers)
    logging.basicConfig(level=logging.ERROR,format='%(levelname)s:%(name)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S',handlers=handlers)
    app.run(host='0.0.0.0', port='3111')
    

