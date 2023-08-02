from functools import wraps
from CS157A.Database.Models.BookList import BookLists
from CS157A.Database.Models.Ratings import BookRatings
from CS157A.Flask import flask_obj
from flask import render_template, request, flash, redirect, url_for, session, g, jsonify
from CS157A.Database.Models.Users import Users
from CS157A.Flask.Sessions import set_user_session
from CS157A.HTTP.GoogleBooksAPI import request_books
from CS157A.Database.Models.Books import Books
from CS157A.Database.Models.UserActivity import UserActivity
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

def get_admin_status():
    return session.get('isAdmin')

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

def admin_access_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        g.authenticated = is_logged_in()
        g.admin = get_admin_status()
        if g.authenticated and g.admin:
            g.user_email = get_user_email()
            g.user_first_name = get_user_first_name()
            g.user_id = get_user_id()
            return f(*args, **kwargs)
        else:
            return "You need admin access to view this page...."

    return decorated_function


@flask_obj.before_request
def before_request():
    g.authenticated = is_logged_in()
    g.admin = get_admin_status()
    if g.authenticated:
        g.user_email = get_user_email()
        g.user_first_name = get_user_first_name()
        g.user_id = get_user_id()

@flask_obj.route('/', methods=["GET"])
def home_page():
    return render_template('HomePage.html')

#
# ____________________Account/Session Managements_________________________
#

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
            isAdmin=False
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
            isAdmin = loginResponse[3]
            set_user_session(email=email, first_name=first_name, user_id=user_id, isAdmin=isAdmin)
            UserActivity().add_activity(user_id=user_id, activity_type="LOGIN", activity_msg="LOGGED INTO YOUR ACCOUNT")
            return redirect(url_for('home_page'))

    return render_template('LoginPage.html')

@flask_obj.route("/logout", methods=['GET'])
@login_required
def logout():
    UserActivity().add_activity(user_id=g.user_id, activity_type="LOG OUT", activity_msg="LOGGED OUT OF YOUR ACCOUNT")
    session.clear()
    return redirect(url_for('home_page'))

@flask_obj.route('/user-profile', methods=["GET"])
@login_required
def user_profile_page():
    userInformation = Users().get_user_information(user_id=g.user_id, email=g.user_email)
    read_later_list = BookLists().get_user_read_later(user_id=g.user_id)
    activity_list = UserActivity().get_all_activities(user_id=g.user_id)

    if(userInformation is None):
        return "Go back and retry... [NO_USER_INFORMATION_LOADED | TRY_CLEARING_COOKIES]"
    return render_template('UserProfile.html', userInformation=userInformation, read_later_list=read_later_list, activity_list=activity_list)


# ________________Database Calls/API_________________________

# 
# Search/Selects
# 

#  ________________NAVBAR ITEM________________
@flask_obj.route('/best-sellers', methods=["GET"])
def best_sellers_page():
    return render_template('BestSellers.html')

#  ________________NAVBAR ITEM________________
@flask_obj.route('/advanced-search', methods=["GET"])
def advanced_search_page():
    return render_template('AdvancedSearch.html')

#  ________________NAVBAR ITEM________________
@flask_obj.route('/all-books', methods=["GET"])
def all_books_page():
    response = Books().get_all_books()
    book_list = response[0]
    book_count = response[1]
    return render_template("ViewBooks.html", books=book_list, book_count=book_count)

#  ________________NAVBAR ITEM________________
@flask_obj.route('/search-by-category', methods=["GET"])
def search_by_category_page():
    categories = Books().get_all_book_genres()
    return render_template('SearchByCategory.html', categories=categories)

#  ________________NAVBAR ITEM________________ (Search Bar)
@flask_obj.route('/search-books', methods=["POST","GET"])
@flask_obj.route('/search-books/<string:search_input>', methods=["POST"])
def search_books_api(search_input=None):

    genre = request.args.get('genre')

    book_name = request.args.get('book_name')
    authors = request.args.get('authors')
    #authors = [author.strip() for author in authors.split(',')] if authors is not None else None
    ISBN = request.args.get('ISBN')
    genres = request.args.get('genres')
    #genres = [genre.strip() for genre in genres.split(',')] if genres is not None else None
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    book_type = request.args.get('book_type')
    page_min = request.args.get('page_min')
    page_max = request.args.get('page_max')
    include_unknown = request.args.get('include_unknown') == 'on'

    if(genre):
        response = Books().get_books_off_genre(genre=genre)
        book_list = response[0]
        book_count = response[1]
        # response = Books().get_books(book_name="1984",debug=True)
        # book_list = response[0]
        # book_count = response[1]

    elif (search_input):
        response = Books().get_books_off_search(search_input)
        book_list = response[0]
        book_count = response[1]

    else:
        response = Books().get_books(
            book_name=book_name,
            author_names=authors.split(',') if authors else None,
            ISBN=ISBN,
            start_date=start_date,
            end_date=end_date,
            genres=genres.split(',') if genres else None,
            book_type=book_type,
            page_min=page_min,
            page_max=page_max,
            include_nulls=include_unknown,
            debug=True #TODO remove when done with bugfixing
        )
        book_list = response[0]
        book_count = response[1]

    return render_template("ViewBooks.html", books=book_list, book_count=book_count)

@flask_obj.route("/view-book", methods=["GET"])
def get_book_api(isbn_value=None):
    isbn_value = request.args.get('isbn_value')
    if(isbn_value):
        book_data_response = Books().get_specific_book(isbn=isbn_value)
        try:
            book_data_response_title = book_data_response[0]['name']
        except:
            book_data_response_title = "Random Book"
        recommended_books = Books().get_recommended_books(title=book_data_response_title, current_isbn=isbn_value)
    else:
        book_data_response = "GO_BACK_AND_TRY_AGAIN"
        recommended_books = "GO_BACK_AND_TRY_AGAIN"

    user_id = get_user_id()

    total_reviews, user_rating = BookRatings().get_specific_book_ratings_count(book_isbn=isbn_value, user_id=user_id)
    user_rating = int(user_rating)

    return render_template("SpecificBook.html", book_data=book_data_response, recommendations=recommended_books, total_reviews=total_reviews, user_rating=user_rating)



# 
# Add/Inserts
# 

@flask_obj.route('/add-books', methods=["GET", "POST"])
@flask_obj.route('/add-books/<string:search_input>', methods=["POST"])
@admin_access_only
def request_google_books_api(search_input=None):
    if request.method == "POST":
        search_input = request.form.get('search_input')
        if search_input:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response = loop.run_until_complete(request_books(search_input))
            flash(f"STATUS: ADDED {response.get('BOOKS_ADDED')} BOOKS")
            UserActivity().add_activity(user_id=g.user_id, activity_type="ADDED BOOKS [ADMIN]", activity_msg=f"ADDED BOOKS|SEARCH INPUT: {search_input}")

        else:
            flash("Please provide a valid search input.")
        return redirect(url_for('request_google_books_api'))
    
    return render_template('AddBook.html')


@flask_obj.route('/add-to-read-later', methods=["POST"])
@login_required
def add_to_read_later_api():
    if(request.method == "POST"):
        user_id = g.user_id
        book_isbn = request.form.get('book_isbn')
        response = BookLists().add_to_read_later(user_id=user_id, book_isbn=book_isbn)
        if(response):
            UserActivity().add_activity(user_id=g.user_id, activity_type="READ LATER", activity_msg=f"ADDED BOOK: {book_isbn}")
            return jsonify({"Success": True, "isLoggedIn": is_logged_in()})
        else:
            return jsonify({"Success": False, "isLoggedIn": is_logged_in()})

@flask_obj.route('/add-book-rating', methods=["POST"])
@login_required
def add_book_rating_api():
    if(request.method == "POST"):
        user_id = g.user_id
        book_isbn = request.form.get('book_isbn')
        rating_value = request.form.get('rating_value')
        BookRatings().add_rating(user_id=user_id, book_isbn=book_isbn, rating_value=rating_value)
        print(user_id)
        print(book_isbn)
        print(rating_value)
    return jsonify({"Success": "ADDED RATING"})

#   
# Remove/Delete
# 
@flask_obj.route("/remove-read-later-book", methods=["POST"])
def remove_read_later_api():
    if(request.method == "POST"):
        book_isbn = request.form.get('book_isbn')
        remove_response = BookLists().remove_from_read_later(user_id=g.user_id, isbn=book_isbn)
        UserActivity().add_activity(user_id=g.user_id, activity_type="READ LATER", activity_msg=f"REMOVED BOOK: {book_isbn}")
        return jsonify({
            "REMOVE_RESPONSE": remove_response
        })