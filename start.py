from collections import namedtuple
from datetime import datetime

from flask import Flask, render_template, redirect, url_for, request


UPLOAD_FOLDER = '/path/to/the/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

File = namedtuple('File', 'name date time valid id')
files = []
User = namedtuple('User', 'username files id')
users = []


# root directory
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/user', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['username']
        user_id = user_exist(name, users)
        if user_id >= 0:
            return redirect(url_for('index'))
        else :
            user = User(name, [], len(users))
            users.append(user)
            return redirect(url_for('main', user_id=user.id))
    elif request.method == 'GET':
        nick = request.args.get('username')
        user_id = user_exist(nick, users)
        if user_id >= 0:
            return redirect(url_for('main', user_id=user_id))
        else:
            return redirect(url_for('index'))


@app.route('/main/<int:user_id>', methods=['GET'])
def main(user_id):
    return render_template('main.html', user=users[user_id])


#   receive file form data and id of user
#   crete new file list and new user tuple
#   replace old user tuple with new one
#   redirect to mainpage and list all files
@app.route('/add_file', methods=['POST'])
def add_file():
    #get new File data from FORM
    file_name = request.form['file-name']
    live_date = request.form['live-date']
    live_time = request.form['live-time']
    valid = compare_time(live_date, live_time)
    user_id = int(request.form['id'])
#   get current user obj
    c_us = users[user_id]
#   create new array of files
    fileses = users[user_id].files
    fileses.append(File(file_name, live_date, live_time, valid, len(users[user_id].files)))
    # create copy of User obj with new array of files
    n_us = User(c_us.username, fileses, user_id)
    users[user_id] = n_us
    return redirect(url_for('main', user_id=n_us.id))


#   receive user_id and file_id
#   check if current file out of date
#   update user profile and return file page or 404error page
@app.route('/file/<int:user_id>/<int:file_id>', methods=['GET'])
def get_file_date(user_id, file_id):
    user = users[user_id]
    valid_for_now = compare_time(user.files[file_id].date, user.files[file_id].time)
    user.files[file_id] = File(user.files[file_id].name, user.files[file_id].date, user.files[file_id].time, valid_for_now, file_id)
    if user.files[file_id].valid:
        return render_template('file.html', user=user, file_id=file_id)
    else:
        return redirect(url_for('/not-found'))


# 404 error page
@app.route('/file_not_found', methods=['GET'])
def file_not_found():
    return render_template('not-found.html')


#   receive date and time of expiration
#   compare with current time
#   return if file have time to live
def compare_time(date, time):
    cd = date.split('-') + time.split(':')
    for i in range(0, len(cd)):
        cd[i] = int(cd[i])
    dead_time = datetime(*cd)
    current_time = datetime.now()
    if dead_time > current_time:
        return True
    else:
        return False

#  receive name to look for and list where to look
#  return position of user with such nickname or return -1
def user_exist(name, array_of_users):
    for us in array_of_users:
        if us.username == name:
            return us.id
    else:
        return -1
