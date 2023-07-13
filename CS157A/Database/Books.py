from CS157A.Database import mydb, mycursor

class Books():
    def __init__(self):
        self.create_books_table(self)

    def create_books_table(self):

        #TODO: set up the action in case of deletion of a book

        # info about books in general
        query0 = """
        CREATE TABLE IF NOT EXISTS BOOKS(
        ISBN VARCHAR(20) PRIMARY KEY, 
        name VARCHAR(128) NOT NULL,
        description VARCHAR(1024),                  -- for now can be null
        publish_date DATE,                           -- for now can be null
        type ENUM('PHYSICAL', 'DIGITAL') NOT NULL,
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





