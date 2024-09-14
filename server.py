from werkzeug.utils import secure_filename
from flask import Flask, request, render_template, g
import datetime
import os
import random
import sqlite3

DATABASE = 'quickchan.db'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__, static_url_path='/static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def dict_factory(cursor, row):
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = dict_factory
    return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def create_new_post(data, reply_id):
    if reply_id == '0':
        query = ''' INSERT INTO posts(image_file, user, date, board, post_text) 
                    VALUES (?, ?, ?, ?, ?) '''
    else:
        query = ''' INSERT INTO replies(user, date, board, post_text, replying_to) 
                    VALUES (?, ?, ?, ?, ?) '''  # Removed reply_image
    cur = get_db().cursor()
    cur.execute(query, data)
    get_db().commit()
    cur.close()
    return cur.lastrowid

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/b/<board>/post', methods=['POST'])
def post(board):
    newfilename = ''
    if request.form.get('post_text'):
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                newfilename = f"{random.randint(10000000, 100000000)}.{filename.rsplit('.', 1)[1].lower()}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], newfilename))
        now = datetime.datetime.now()
        post = (newfilename, request.form.get('name'), now.isoformat(), board, request.form.get('post_text'))
        create_new_post(post, '0')
    return 'posted'

@app.route('/b/<board>/post_reply/<int:post_id>', methods=['POST'])
def post_reply(board, post_id):
    if request.form.get('post_text'):
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                newfilename = f"{random.randint(10000000, 100000000)}.{filename.rsplit('.', 1)[1].lower()}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], newfilename))
        now = datetime.datetime.now()
        reply = (request.form.get('name'), now.isoformat(), board, request.form.get('post_text'), post_id)  # Removed newfilename
        create_new_post(reply, post_id)
    return 'posted'

@app.route('/newboard/', methods=['GET', 'POST'])
def newboard():
    if request.method == 'GET':
        return render_template('newboard.html')
    name = request.form.get('board_name')
    desc = request.form.get('board_description')
    category = request.form.get('category')
    
    if name and desc and category:
        existing_board = query_db('SELECT * FROM boards WHERE board_short_name = ?', [name], one=True)
        if existing_board:
            return 'Board with this name already exists!', 400

        query = "INSERT INTO boards (board_short_name, board_description, category) VALUES (?, ?, ?)"
        cur = get_db().cursor()
        cur.execute(query, (name, desc, category))
        get_db().commit()
        cur.close()
        return 'Board created successfully!'
    return 'Board name, description, and category are required!', 400

@app.route('/')
def index():
    boards = query_db('SELECT * FROM boards')
    categories = {}
    
    for board in boards:
        category = board['category']
        categories.setdefault(category, []).append(board)

    return render_template('front.html', categories=categories)

@app.route('/b/<board>')
def board(board):
    board_data = query_db('SELECT * FROM boards WHERE board_short_name = ?', [board], one=True)
    if board_data is None:
        return "Board not found", 404

    posts = query_db('SELECT * FROM posts WHERE board = ?', [board])
    return render_template('board.html', posts=posts, board=board, board_desc=board_data['board_description'])

@app.route('/b/<board>/reply/<int:post_id>')
def reply(board, post_id):
    post = query_db('SELECT * FROM posts WHERE post_id = ?', [post_id], one=True)
    replies = query_db('SELECT * FROM replies WHERE replying_to = ?', [post_id])
    return render_template('reply.html', post=post, replies=replies, board=board)

if __name__ == "__main__":
    app.run(debug=True)