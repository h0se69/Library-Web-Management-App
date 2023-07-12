from functools import wraps
from CS157A.Flask import flask_obj
from flask import render_template, request, flash, redirect, url_for, session, g
from CS157A.Database.Models.Users import Users
from CS157A.Flask.Sessions import set_user_session


flask_obj.secret_key = 'test-key'

# # # Will move to sessions file later
def is_logged_in():
    return session.get('authenticated', False)

def get_user_email():
    return session.get('email')

def get_user_first_name():
    return session.get('first_name')

def get_user_id():
    return session.get('user_id')

def isLoggedIn(f):
    @wraps(f)
    def decorated_function(*args, **kwards):
        g.authenticated = is_logged_in()
        g.user_email = get_user_email()
        g.user_first_name = get_user_first_name()
        g.user_id = get_user_id()
        return f(*args, **kwards)

    return decorated_function

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwards):
        g.authenticated = is_logged_in()
        if g.authenticated:
            g.user_email = get_user_email()
            g.user_first_name = get_user_first_name()
            g.user_id = get_user_id()
            return f(*args, **kwards)
        else:
            return redirect(url_for('login_page'), code=302)
    return decorated_function
# # #

@flask_obj.route('/', methods=["GET"])
@isLoggedIn
def home_page():
    return render_template('HomePage.html')

@flask_obj.route('/register', methods=["GET", "POST"])
@isLoggedIn
def register_page():
    if(request.method=="POST" and all(key in request.form for key in ['email', 'first_name', 'last_name', 'password'])):
        email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        password = request.form['password']

        register_response = Users().register_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )
        if(register_response == True):
            return redirect(url_for('login_page'))
        else:
            flash(f"ERROR: {register_response}")

    return render_template('RegisterPage.html')

@flask_obj.route('/login', methods=["GET", "POST"])
@isLoggedIn
def login_page():
    if(request.method == "POST" and all(key in request.form for key in ["email", "password"])):
        email = request.form["email"]
        password = request.form["password"]
        loginResponse = Users().authenticate_user(email=email, password=password)
        
        if(loginResponse == False):
            flash("Invalid Login Credentials")
        else:
            first_name = loginResponse[0]
            email = loginResponse[1]
            user_id = loginResponse[2]
            set_user_session(email=email, first_name=first_name, user_id=user_id)
            return redirect(url_for('home_page'))

    return render_template('LoginPage.html')

@flask_obj.route("/logout", methods=['GET'])
@isLoggedIn
def logout():
    session.clear()
    return redirect(url_for('home_page'))

@flask_obj.route('/search-by-category', methods=["GET"])
@isLoggedIn
def search_by_category_page():
    return render_template('SearchByCategory.html')

@flask_obj.route('/best-sellers', methods=["GET"])
@isLoggedIn
def best_sellers_page():
    return render_template('BestSellers.html')

@flask_obj.route('/all-books', methods=["GET"])
@isLoggedIn
def all_books_page():
    return render_template('AllBooks.html')

@flask_obj.route('/user-profile', methods=["GET"])
@login_required
def user_profile_page():
    userInformation = Users().get_user_information(user_id=g.user_id, email=g.user_email)
    if(userInformation is None):
        return "Go back and retry..."
    return render_template('UserProfile.html', userInformation=userInformation)