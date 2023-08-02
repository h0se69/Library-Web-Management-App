from typing import Optional
from CS157A.Database import mydb, mycursor
import mysql.connector.errors


class Books():
    def __init__(self):
        self.create_books_table()
        
    def create_books_table(self):

        #TODO: set up the action in case of deletion of a book

        # info about books in general
        query0 = """
        CREATE TABLE IF NOT EXISTS BOOKS(
            ISBN VARCHAR(20) PRIMARY KEY, 
            name VARCHAR(500) NOT NULL,
            description VARCHAR(4096),          -- for now can be null
            publish_date DATE,                  -- for now can be null
            page_amt INTEGER,                   -- for now can be null
            type ENUM('PHYSICAL', 'DIGITAL') NOT NULL,
            image VARCHAR(1024) NULL -- can be null incase no image is provided
        );
        """

        # for the books in the library 
        # can have multiple books of the same isbn  
        query1 = """
            CREATE TABLE IF NOT EXISTS LIBRARY_BOOKS(
            book_id INTEGER PRIMARY KEY AUTO_INCREMENT,
            ISBN VARCHAR(20) NOT NULL,                   
            CONSTRAINT fk_book_library FOREIGN KEY(ISBN) REFERENCES BOOKS(ISBN)
        );
        """

        # genre of books
        query2 = """
        CREATE TABLE IF NOT EXISTS BOOK_GENRES(
            ISBN VARCHAR(20) NOT NULL,                   
            genre VARCHAR(255) NOT NULL, 
            PRIMARY KEY (ISBN, genre),    
            CONSTRAINT fk_book_genre FOREIGN KEY(ISBN) REFERENCES BOOKS(ISBN)                                             
        );
        """

        # author of books (books can have multiple authors)
        query3 = """
        CREATE TABLE IF NOT EXISTS BOOK_AUTHORS(
            ISBN VARCHAR(20) NOT NULL,                   
            author VARCHAR(512) NOT NULL, 
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
    def add_book(self, isbn:str, name:str, book_type:str, description: str=None, publish_date:str=None, page_amount:int=None, image:str=None):
        name = name[0:499]
        try:
            query = f"""
                INSERT INTO BOOKS (ISBN, name, description, publish_date, type, page_amt, image)
                VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            mycursor.execute(query, (isbn, name, description, publish_date, book_type, page_amount, image))
            mydb.commit()
        except mysql.connector.errors.IntegrityError as duplicateBook:
            print(f"duplicateBook_Error_add_book: {duplicateBook}")

    def add_library_book(self, isbn:str):
        try:
            query = f"""
                INSERT INTO LIBRARY_BOOKS (ISBN)
                VALUES (%s)"""
            mycursor.execute(query, (isbn,))
            mydb.commit()
        except mysql.connector.errors.IntegrityError as duplicateBook:
            print(f"duplicateBook_Error_add_library_book: {duplicateBook}")

    def add_book_author(self, isbn:str, author_s:str):
        try:
            query = f"""
                INSERT INTO BOOK_AUTHORS (ISBN, author)
                VALUES (%s, %s)"""
            mycursor.execute(query, (isbn, author_s))
            mydb.commit()
        except mysql.connector.errors.IntegrityError as duplicateBook:
            print(f"duplicateBook_Error_add_book_author: {duplicateBook}")

    def add_book_genres(self, isbn:str, genre:str):
        try:
            query = f"""
                INSERT INTO BOOK_GENRES (ISBN, genre)
                VALUES (%s, %s)"""
            mycursor.execute(query, (isbn, genre))
            mydb.commit()
        except mysql.connector.errors.IntegrityError as duplicateBook:
            print(f"duplicateBook_Error_add_book_genres: {duplicateBook}")


    def get_all_books(self):
        query = f"""
            SELECT * 
            FROM BOOKS
            JOIN BOOK_AUTHORS ON BOOKS.ISBN = BOOK_AUTHORS.ISBN
        """
        mycursor.execute(query)
        response = mycursor.fetchall()
        book_count = len(response)
        
        columns = [column[0] for column in mycursor.description]
        response_dict = [dict(zip(columns, row)) for row in response]
        return response_dict, book_count # list response | book count

    def get_books_off_search(self, search_value:str):
        query = f"""
            SELECT *
            FROM BOOKS
            JOIN BOOK_AUTHORS ON BOOKS.ISBN = BOOK_AUTHORS.ISBN
            WHERE name LIKE %s
        """
        mycursor.execute(query, (f"%{search_value}%", ))

        response = mycursor.fetchall()
        columns = [column[0] for column in mycursor.description]
        response_dict = [dict(zip(columns, row)) for row in response]

        book_count = len(response)
        return response_dict, book_count # list response | book count
    
    def get_books_off_genre(self, genre):
        query = f"""
            SELECT DISTINCT *
            FROM BOOKS B
            JOIN BOOK_AUTHORS BA 
                ON B.ISBN=BA.ISBN
            JOIN BOOK_GENRES BG 
                ON B.ISBN=BG.ISBN
            WHERE BG.genre='{genre}'
        """
        mycursor.execute(query)

        response = mycursor.fetchall()
        columns = [column[0] for column in mycursor.description]
        response_dict = [dict(zip(columns, row)) for row in response]

        book_count = len(response)
        return response_dict, book_count # list response | book count

    def get_all_book_genres(self):
        query = f"""
            SELECT DISTINCT genre
            FROM BOOK_GENRES
            ORDER BY genre
        """
        mycursor.execute(query,)
        response = mycursor.fetchall()
        removed_tuples_response = [genre[0] for genre in response]
        return removed_tuples_response

    def get_specific_book(self, isbn:str):
        query = f"""
            SELECT *
            FROM BOOKS B
            JOIN BOOK_AUTHORS BA 
                ON B.ISBN=BA.ISBN
            JOIN BOOK_GENRES BG
                ON B.ISBN=BG.ISBN
            JOIN LIBRARY_BOOKS LB 
                ON B.ISBN=LB.ISBN
            WHERE B.ISBN='{isbn}'
        """
        mycursor.execute(query,)
        response = mycursor.fetchall()
        columns = [col[0] for col in mycursor.description]
        dict_response = [dict(zip(columns, row)) for row in response]

        return dict_response


    def get_recommended_books(self, title:str, current_isbn:str):
        title = title.split(" ")[0]
        query = f"""
            SELECT *
            FROM BOOKS B
            WHERE B.name LIKE %s AND B.ISBN != %s
            ORDER BY RAND() 
            LIMIT 3
        """
        mycursor.execute(query, (f"%{title}%", current_isbn))
        response = mycursor.fetchall()
        columns = [col[0] for col in mycursor.description]
        dict_response = [dict(zip(columns, row)) for row in response]

        return dict_response


    # Limited to 100 results
    # By default returns all books
    # WARNING: This uses AND for everything (not OR)
    # ISBN is book ISBN
    # Has date range, if one is not provided asumes before / after
    # Page range acts the same as date range
    # Supports list of authors
    # Supports lists of genres 
    # book_type should either be 'digital' or 'physical', otherwise ignored
    #
    # TODO NEEDS TESTING
    def get_books(self, book_name=None, author_names=None, ISBN=None, start_date=None, end_date=None, page_min=None, page_max=None, genres=None, book_type=None, include_nulls =False, debug = False):
        query = """SELECT DISTINCT * \nFROM Books \nWHERE 1=1\n"""

        if ISBN:
            query += f" AND ISBN = '{ISBN}'\n"
        else:    
            if book_name:
                query += f" AND name LIKE '%{book_name}%'\n"

            if author_names:
                for author in author_names:
                    query += f" AND EXISTS (SELECT 1 FROM Book_Authors WHERE Books.ISBN = Book_Authors.ISBN AND author = '{author}')\n"
                    # needs to be checked
                    # probably should be rewritten because efficiency

            if start_date and end_date:
                query += f" AND (publish_date BETWEEN '{start_date}' AND '{end_date}'" + " OR publish_date IS NULL)\n" if include_nulls else ")\n"
            elif start_date:
                query += f" AND (publish_date >= '{start_date}'" + " OR publish_date IS NULL)\n" if include_nulls else ")\n"
            elif end_date:
                query += f" AND (publish_date <= '{end_date}'" + " OR publish_date IS NULL)\n" if include_nulls else ")\n"

            if page_min and page_max:  
                query += f" AND (page_amt BETWEEN '{page_min}' AND '{page_max}'" + " OR page_amt IS NULL)\n" if include_nulls else ")\n"
            elif page_min:
                query += f" AND (page_amt >= {page_min}" + " OR page_amt IS NULL)\n" if include_nulls else ")\n"
            elif page_max:
                query += f" AND (page_amt <= {page_max}" + " OR page_amt IS NULL)\n" if include_nulls else ")\n"

            if genres:
                # query += f" AND EXISTS (SELECT 1 FROM Genres WHERE Books.ISBN = Genres.ISBN AND genre IN ({', '.join(['%s']*len(genres))}))" this is OR not AND
                for genre in genres:
                    query += f" AND EXISTS (SELECT 1 FROM Book_Genres WHERE Books.ISBN = Book_Genres.ISBN AND genre = '{genre}')\n"
                # probably should be rewritten because efficiency

            if book_type:
                book_type = book_type.upper()
                if book_type == 'PHYSICAL' or book_type == 'DIGITAL':
                    # query += f" AND b.type = '{book_type}' \n"
                    query += f" AND Books.type = '{book_type}' \n" #Changes from b.type to Books.type

        query+=" LIMIT 100"

        if debug == True:
            print()
            print(query)
            print()

        mycursor.execute(query)   
        response = mycursor.fetchall()

        if debug == True:
            print(response)

        columns = [column[0] for column in mycursor.description]
        response_dict = [dict(zip(columns, row)) for row in response]

        book_count = len(response)
        return response_dict, book_count
    