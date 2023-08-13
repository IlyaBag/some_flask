from flask import Flask, request, Response, make_response, session
from flask import render_template, url_for, flash, get_flashed_messages, redirect
import json
from functools import reduce
# from data import UserRepository


# users = ['mike', 'mishel', 'adel', 'keks', 'kamila']


# Это callable WSGI-приложение
app = Flask(__name__)

app.secret_key = 'secret_key'


@app.route('/')
def hello_world():
    return '''<h1>Welcome to Flask!</h1>\n
            My 1st Flask app with <a href=/users>link</a>'''
    # return 42  # raise exception


@app.get('/users')
def users_get():
    # users = get_users_from_file()
    users = get_cookied_users()
    term = request.args.get('term', '')
    filtered_users = [user for user in users if term in user['nickname']]
    messages = get_flashed_messages(with_categories=True)
    return render_template(
        'users/index.html',
        users=filtered_users,
        messages=messages
        )


@app.route('/users/<id>')
def get_user(id):
    return render_template(
        'users/show.html',
        name=id,
    )


@app.route('/users/new')
def users_new():
    user = {
        'id': None,
        'nickname': '',
        'email': ''
    }
    errors = {}
    return render_template(
        'users/new.html',
        user=user,
        errors=errors
    )


@app.post('/users')
def users_post():
    user = request.form.to_dict()
    errors = validate(user)
    if errors:
        messages = get_flashed_messages(with_categories=True)
        return render_template(
            'users/new.html',
            user=user,
            errors=errors,
            messages=messages,
        )
    # data = []
    # data = get_users_from_file()
    data = get_cookied_users()
    if data:
        max_id = reduce(lambda y, x: x.get('id') if x.get('id') > y else y, data, 0)
    else:
        max_id = 0
    id = {'id': max_id + 1}
    user.update(id)
    data.append(user)
    # with open('user_data', 'w') as repo:
    #     repo.write(json.dumps(data))
    response = make_response(redirect(url_for('users_get')))
    response.set_cookie('users', json.dumps(data))
    return response


@app.route('/users/<int:id>/edit')
def edit_user(id):
    # all_users = get_users_from_file()
    all_users = get_cookied_users()
    user = list(filter(lambda u: u['id'] == id, all_users))[0]
    errors = {}
    return render_template(
        'users/edit.html',
        user=user,
        errors=errors
    )


@app.route('/users/<int:id>/patch', methods=['POST'])
def patch_user(id):
    all_users = get_cookied_users()
    user = list(filter(lambda u: u['id'] == id, all_users))[0]
    data = request.form.to_dict()

    errors = validate(data)
    if errors:
        return render_template(
            '/users/edit.html',
            user=user,
            errors=errors
        ), 422
    
    for key in data:
        user[key] = data[key]
    for item in all_users:
        if item['id'] == id:
            item.update(user)
    
    # with open('user_data', 'w') as repo:
    #     repo.write(json.dumps(all_users))

    response = make_response(redirect(url_for('users_get')))
    response.set_cookie('users', json.dumps(all_users))

    flash('User has been updated', 'success')
    return response


@app.route('/users/<int:id>/delete')
def get_delete_user(id):
    return render_template('users/delete.html', id=id)


@app.post('/users/<int:id>/delete')
def delete_user(id):
    # all_users = get_users_from_file()
    all_users = get_cookied_users()
    all_users_after_delete = list(filter(lambda u: u['id'] != id, all_users))
    # with open('user_data', 'w') as repo:
    #     repo.write(json.dumps(all_users_after_delete))
    response = make_response(redirect(url_for('users_get')))
    response.set_cookie('users', json.dumps(all_users_after_delete))
    flash(f'User {id} has been deleted', 'success')
    return response
    

@app.get('/login')
def login():
    email = ''
    errors={}
    return render_template(
        'users/login.html',
        email_to_login=email,
        errors=errors,
    )

@app.post('/login')
def logging_in():
    email_to_login = request.form.get('login')
    all_users = get_cookied_users()
    for user in all_users:
        if email_to_login == user['email']:
            session['logged_user'] = user['nickname']
            flash(f'User {email_to_login} has been logged in')
            return redirect(url_for('users_get'))
    else:
        errors = {'no_user': f'There is no user with email {email_to_login}'}
        return render_template(
            'users/login.html',
            email_to_login=email_to_login,
            errors=errors,
            # messages=messages
        )


@app.post('/logout')
def logout():
    session.clear()
    flash('You have been logged out')
    return redirect(url_for('users_get'))


def validate(data):
    errors = {}
    for k, v in data.items():
        if v == '':
            errors[k] = "Can't be blank"
    if 1 <= len(data['nickname']) <= 4:
        errors['nickname'] = 'Nickname must be grater than 4 characters'
    return errors


def get_users_from_file():
    with open('user_data', 'r') as f:
        users_data = json.load(f)
    return users_data


def get_cookied_users():
    return json.loads(request.cookies.get('users', json.dumps([])))
