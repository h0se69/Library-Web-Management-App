from typing import Optional
from CS157A.Database import mydb, mycursor
import mysql.connector.errors


class Books():
    def __init__(self):
        self.books_table = "BOOKS"
        self.library_books_table = "LIBRARY_BOOKS"
        self.books_genre_table = "BOOK_GENRES"
        self.books_authors_table = "BOOK_AUTHORS"
        self.create_books_table()
        
    def create_books_table(self):

        #TODO: set up the action in case of deletion of a book

        # info about books in general
        query0 = """
        CREATE TABLE IF NOT EXISTS BOOKS(
            ISBN VARCHAR(20) PRIMARY KEY, 
            name VARCHAR(255) NOT NULL,
            description VARCHAR(4096),                  -- for now can be null
            publish_date DATE,                           -- for now can be null
            type ENUM('PHYSICAL', 'DIGITAL') NOT NULL
        );
        """

        # for the books in the library 
        # can have multiple books of the same isbn  
        query1 = """
        CREATE TABLE IF NOT EXISTS LIBRARY_BOOKS(
            book_id INTEGER PRIMARY KEY AUTO_INCREMENT,
            ISBN VARCHAR(20) NOT NULL,                  -- I remember there is ISBN 10, 
                                                        -- ISBN 13 and they have dashes, this might
                                                        -- change depending on data scraping
            -- page_amt INTEGER NOT NULL -- add later if scraping allows                
            
            CONSTRAINT fk_book_library FOREIGN KEY(ISBN) REFERENCES BOOKS(ISBN)
        );
        """

        # genre of books
        query2 = """
        CREATE TABLE IF NOT EXISTS BOOK_GENRES(
            ISBN VARCHAR(20) NOT NULL,                   
            genre VARCHAR(32) NOT NULL, 
            PRIMARY KEY (ISBN, genre),    
            CONSTRAINT fk_book_genre FOREIGN KEY(ISBN) REFERENCES BOOKS(ISBN)                                             
        );
        """

        # author of books (books can have multiple authors)
        query3 = """
        CREATE TABLE IF NOT EXISTS BOOK_AUTHORS(
            ISBN VARCHAR(20) NOT NULL,                   
            author VARCHAR(128) NOT NULL, 
            PRIMARY KEY (ISBN, author),    
            CONSTRAINT fk_book_author FOREIGN KEY(ISBN) REFERENCES BOOKS(ISBN)                                             
        );
        """
        mycursor.execute(query0)
        mycursor.execute(query1)
        mycursor.execute(query2)
        mycursor.execute(query3)

    # watch the argument order when adding
    # needed to move descrip/date to end due to default value None
    def add_book(self, isbn:str, name:str, book_type:str, description: str=None, publish_date:str=None):
        try:
            query = f"""
                INSERT INTO {self.books_table} (ISBN, name, description, publish_date, type)
                VALUES (%s, %s, %s, %s, %s)"""
            mycursor.execute(query, (isbn, name, description, publish_date, book_type))
            mydb.commit()
        except mysql.connector.errors.IntegrityError as duplicateBook:
            print(f"duplicateBook_Error: {duplicateBook}")


    def get_all_books(self):
        query = f"""
            SELECT * 
            FROM {self.books_table}
        """
        mycursor.execute(query)
        response = mycursor.fetchall()
        book_count = len(response)

        return response, book_count # list response | book count

    def get_books_off_search(self, search_value:str):
        query = f"""
            SELECT *
            FROM {self.books_table}
            WHERE name LIKE %s OR ISBN LIKE %s
        """
        mycursor.execute(query, (f"%{search_value}%", f"%{search_value}%"))
        response = mycursor.fetchall()
        book_count = len(response)
        return response, book_count # list response | book count