from functools import wraps
from CS157A.Database.Models.BookList import BookLists
from CS157A.Flask import flask_obj
from flask import render_template, request, flash, redirect, url_for, session, g, jsonify
from CS157A.Database.Models.Users import Users
from CS157A.Flask.Sessions import set_user_session
from CS157A.HTTP.GoogleBooksAPI import request_books
from CS157A.Database.Models.Books import Books
import asyncio


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

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        g.authenticated = is_logged_in()
        if g.authenticated:
            g.user_email = get_user_email()
            g.user_first_name = get_user_first_name()
            g.user_id = get_user_id()
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login_page'))

    return decorated_function

@flask_obj.before_request
def before_request():
    g.authenticated = is_logged_in()
    if g.authenticated:
        g.user_email = get_user_email()
        g.user_first_name = get_user_first_name()
        g.user_id = get_user_id()

# # #

@flask_obj.route('/', methods=["GET"])
def home_page():
    return render_template('HomePage.html')

@flask_obj.route('/register', methods=["GET", "POST"])
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
@login_required
def logout():
    session.clear()
    return redirect(url_for('home_page'))

@flask_obj.route('/search-by-category', methods=["GET"])
def search_by_category_page():
    categories = Books().get_all_book_genres()
    return render_template('SearchByCategory.html', categories=categories)

@flask_obj.route('/best-sellers', methods=["GET"])
def best_sellers_page():
    return render_template('BestSellers.html')

@flask_obj.route('/advanced-search', methods=["GET"])
def advanced_search_page():
    return render_template('AdvancedSearch.html')

@flask_obj.route('/all-books', methods=["GET"])
def all_books_page():
    response = Books().get_all_books()
    book_list = response[0]
    book_count = response[1]
    return render_template("ViewBooks.html", books=book_list, book_count=book_count)

@flask_obj.route('/user-profile', methods=["GET"])
@login_required
def user_profile_page():
    userInformation = Users().get_user_information(user_id=g.user_id, email=g.user_email)

    read_later_list = BookLists().get_user_read_later(user_id=g.user_id)

    if(userInformation is None):
        return "Go back and retry..."
    return render_template('UserProfile.html', userInformation=userInformation, read_later_list=read_later_list)

@flask_obj.route('/add-books/<string:search_input>', methods=["GET", "POST"])
@login_required
def request_google_books_api(search_input:str):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    response = loop.run_until_complete(request_books(search_input))
    return response

@flask_obj.route('/add-to-read-later', methods=["POST"])
@login_required
def add_to_read_later_api():
    if(request.method == "POST"):
        user_id = g.user_id
        book_isbn = request.form.get('book_isbn')
        response = BookLists().add_to_read_later(user_id=user_id, book_isbn=book_isbn)
        if(response):
            return jsonify({"Success": True, "isLoggedIn": is_logged_in()})
        else:
            return jsonify({"Success": False, "isLoggedIn": is_logged_in()})


@flask_obj.route('/search-books', methods=["POST"])
@flask_obj.route('/search-books/<string:search_input>', methods=["POST"])
def search_books_api(search_input=None):
    genre = request.args.get('genre')
    if(genre):
        response = Books().get_books_off_genre(genre=genre)
        book_list = response[0]
        book_count = response[1]
    else:
        response = Books().get_books_off_search(search_input)
        book_list = response[0]
        book_count = response[1]

    return render_template("ViewBooks.html", books=book_list, book_count=book_count)
