import asyncio
from datetime import datetime
import json
import os
import uuid
from dotenv import load_dotenv
import httpx
from CS157A.Database.Models.Books import Books
import time    



load_dotenv('.env')

API_KEY = os.getenv('GOOGLE_BOOKS_API_KEY')

google_books_headers = {
    'Accept': 'application/json',
}
google_books_params = {"maxResults": 40} # 40 is the max i think


async def request_books(search_value:str):
    async with httpx.AsyncClient(http2=True) as session:
        google_books_api_url = f"https://www.googleapis.com/books/v1/volumes?q={search_value}&key={API_KEY}&printType=books"
        api_response = await session.get(url=google_books_api_url, headers=google_books_headers, params=google_books_params)
        json_response = check_valid_response(api_response)
        
        if(json_response):
            parsedData = parse_book_data(json_response=json_response)
            return {
                "RESPONSE_CODE": 200,
                "DATA": parsedData
            }
        else:
            return {
                "RESPONSE_CODE": 302,
                "DATA": "INVALID_JSON_RESPONSE"
            }


def parse_book_data(json_response: json):
    data = []
    books = json_response['items']
    BooksObj = Books()

    for book in books:
        volume_info = book.get('volumeInfo', {})
        title = volume_info.get('title', None)
        published_date = get_publish_date(volume_info=volume_info)
        description = volume_info.get('description', None)
        page_count = get_pages(volume_info=volume_info)
        authors_publisher = get_author_publisher(volume_info=volume_info)
        category_genre = get_category_genre(volume_info=volume_info)
        image = get_image(volume_info=volume_info)
        isbn_value = get_isbn(volume_info=volume_info)
        book_type = get_book_type(book_info=book)

        data.append((isbn_value, title, book_type, description, published_date))

        BooksObj.add_book(
            isbn=isbn_value, 
            name=title, 
            book_type=book_type,
            description=description,
            publish_date=published_date,
            page_amount=page_count,
            image=image
            )
        BooksObj.add_library_book(
            isbn=isbn_value
            )
        BooksObj.add_book_author(
            isbn=isbn_value,
            author_s=authors_publisher
            )
        BooksObj.add_book_genres(
            isbn=isbn_value,
            genre=category_genre
            )
    return data

def get_isbn(volume_info: dict):
    industry_identifiers = volume_info.get('industryIdentifiers', None)

    if(industry_identifiers is not None):
        isbn_value = None
        for industry_identifier in industry_identifiers:
            ISBN_13 = "ISBN_13"
            ISBN_10 = "ISBN_10"
            isbn_type = industry_identifier.get('type', None)
            if(isbn_type == ISBN_10):
                isbn_value = industry_identifier.get('identifier', None)
            else:
                isbn_value = str(uuid.uuid4())[0:11] # incase there is no isbn10-13 but other types of identifiers
    else:
        isbn_value = str(uuid.uuid4())[0:11] #no isbn in the data
    
    return isbn_value

def get_pages(volume_info: dict):
    page_count = volume_info.get('pageCount', None)
    if(page_count == "0" or page_count == 0 or None or "None"):
        return None
    else:
        return page_count

def get_image(volume_info: dict):
    image_links = volume_info.get('imageLinks', None)

    if(image_links is not None):
        small_thumbnail = image_links.get("smallThumbnail", None)
    else:
        small_thumbnail = None
    return small_thumbnail

def get_book_type(book_info: dict):
    sale_info = book_info.get('saleInfo', None)

    if(sale_info is not None):
        is_e_book = sale_info.get("isEbook", False)
        if(is_e_book == True):
            book_type = "DIGITAL"
        else:
            book_type = "PHYSICAL"
    else:
        book_type = "DIGITAL"

    return book_type

def get_publish_date(volume_info: dict):
    publish_date_data = volume_info.get('publishedDate', None)

    if(publish_date_data is not None):
        format = check_date_format(publish_date=publish_date_data)
        if(format is None):
            return None
        publish_date_parse = datetime.strptime(publish_date_data, format)
        mysql_date_format = publish_date_parse.strftime("%Y-%m-%d")
        return mysql_date_format
    else:
        return None

def get_author_publisher(volume_info: dict):
    authors_list = volume_info.get('authors', None)
    if(authors_list is not None):
        authors = ",".join(str(author) for author in authors_list)
        return authors
    else:
        publisher = volume_info.get("publisher", None)
        if(publisher is None):
            return "NO_AUTHOR"
        else:
            return publisher

def get_category_genre(volume_info: dict):
    categories_list = volume_info.get('categories', None)
    if(categories_list is not None):
        categories = ",".join(str(category) for category in categories_list)
        return categories
    else:
        return "NO_GENRE"

def check_date_format(publish_date:str):
    formats = [
        "%Y-%m-%d",      # YYYY-MM-DD
        "%d-%m-%Y",      # DD-MM-YYYY
        "%m-%d-%Y",      # MM-DD-YYYY
        "%Y",            # YYYY (year-only)
        "%Y-%m"          # YYYY-MM
    ]
    for format in formats:
            try:
                datetime.strptime(publish_date, format)
                return format
            except ValueError:
                continue
    return None


def check_valid_response(response: httpx.Response):
    response_code = response.status_code
    response_text = response.text
    if(response_code == 200):
        return response.json()
    elif(response_code == 403):
        if("Enable it by visiting https://console.developers.google.com" in response_text):
            print('Enable Books API for your project: https://console.cloud.google.com/apis/api/books.googleapis.com')
        else:
            print(response_text)
        return False
    else:
        print(f"NOT A 200 RESPONSE CODE")
        return False
    
