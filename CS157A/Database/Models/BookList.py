from datetime import datetime
from CS157A.Database import mydb, mycursor
import mysql.connector.errors

class BookLists():

    def __init__(self) -> None:
        self.create_read_later_table()

    def create_read_later_table(self):
        query = f"""
        CREATE TABLE IF NOT EXISTS USERS_READ_LATER(
            user_id INTEGER,
            book_isbn VARCHAR(20),
            date_added DATE NOT NULL,
            FOREIGN KEY (book_isbn) REFERENCES BOOKS(ISBN) ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES Users(user_id) ON UPDATE CASCADE ON DELETE CASCADE,
            CONSTRAINT uc_user_book UNIQUE (user_id, book_isbn)
        )
        """
        mycursor.execute(query)

    
    def add_to_read_later(self, user_id:int, book_isbn:str):
        date_added = datetime.now().date()
        mysql_date_added = date_added.strftime('%Y-%m-%d')
        try:
            query = f"""
                INSERT INTO USERS_READ_LATER (user_id, book_isbn, date_added)
                VALUES (%s, %s, %s)"""
            mycursor.execute(query, (user_id, book_isbn, mysql_date_added))
            mydb.commit()
        except mysql.connector.errors.IntegrityError as duplicateAddLater:
            print(f"Already in read later: {duplicateAddLater}")
            return False
        return True

    def get_user_read_later(self, user_id:int):
        query = f"""
            SELECT B.ISBN, B.name, UR.date_added
            FROM BOOKS B
            JOIN USERS_READ_LATER UR ON B.ISBN = UR.book_isbn
            WHERE UR.user_id={user_id}
            ORDER BY UR.date_added
        """
        mycursor.execute(query)
        response = mycursor.fetchall()
        columns = [col[0] for col in mycursor.description]
        dict_response = [dict(zip(columns, row)) for row in response]

        return dict_response
    
    def remove_from_read_later(self, user_id:int, isbn:str):
        try:
            query = f"""
                DELETE FROM USERS_READ_LATER
                WHERE user_id={user_id} AND book_isbn='{isbn}'
            """
            mycursor.execute(query)
            return True
        except:
            return False