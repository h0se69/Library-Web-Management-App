from CS157A.Flask import flask_obj
from flask import render_template
# from Backend.Database import mydb, mycursor

@flask_obj.route('/', methods=["GET"])
def home_page():
    return render_template('HomePage.html')

@flask_obj.route('/register', methods=["GET", "POST"])
def register_page():
    return render_template('RegisterPage.html')

@flask_obj.route('/login', methods=["GET", "POST"])
def login_page():
    return render_template('LoginPage.html')

@flask_obj.route('/search-by-category', methods=["GET"])
def search_by_category_page():
    return render_template('SearchByCategory.html')

@flask_obj.route('/best-sellers', methods=["GET"])
def best_sellers_page():
    return render_template('BestSellers.html')

@flask_obj.route('/all-books', methods=["GET"])
def all_books_page():
    return render_template('AllBooks.html')