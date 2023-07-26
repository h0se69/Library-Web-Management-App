from typing import Optional
from CS157A.Database import mydb, mycursor
import mysql.connector.errors
from datetime import datetime


class Checkout_Return():
    def __init__(self):
        self.checkout_table = "LIBRARY_CHECKOUT"
        self.fines_table = "LIBRARY_FINES"
        self.book_queue_table = "LIBRARY_BOOK_QUEUE"

        self.create_checkout_return_tables()


    def create_checkout_return_tables(self):

        query1 = f"""CREATE TABLE IF NOT EXISTS {self.checkout_table} (
            checkout_id INTEGER AUTO_INCREMENT,
            user_id INTEGER NOT NULL,
            book_id INTEGER NOT NULL,

            checkout_date DATE NOT NULL,     -- DEFAULT NOW(),
            return_by DATE NOT NULL,         -- could be changed to a generate statement but no experience with them
            returned_date DATE DEFAULT NULL, -- this will keep track of if users returned books

            PRIMARY KEY (checkout_id),
            UNIQUE (user_id, book_id, checkout_date) -- user can check out same book multiple times
            CONSTRAINT fk_library_checkout_book FOREIGN KEY(book_id) REFERENCES LIBRARY_BOOKS(book_id),
            CONSTRAINT fk_library_checkout_user FOREIGN KEY(user_id) REFERENCES USERS(user_id)
        )
        """

        #TODO clarify if we want to give id to  late fees
        query2 = f"""CREATE TABLE IF NOT EXISTS {self.fines_table} (
            checkout_id INTEGER NOT NULL,
            amount DOUBLE NOT NULL,
            reason ENUM('LATE','DAMAGED') NOT NULL,
            paid BIT NOT NULL DEFAULT 0,

            PRIMARY KEY (checkout_id), -- might be wiser to have unique fineid because then user can be fined for late AND damaged books, 
                                       -- if no, it might be an option to combine checkout table and late fees table
            CONSTRAINT fk_library_fines_checkout_id FOREIGN KEY(checkout_id) REFERENCES LIBRARY_CHECKOUT(checkout_id)
        )
        """


        query3 = f"""CREATE TABLE IF NOT EXISTS {self.book_queue_table} (
                user_id INTEGER NOT NULL,
                ISBN VARCHAR(20)
                position INTEGER NOT NULL AUTO_INCREMENT, -- this will keep adding on last, even if initail int like (0) is gone, so all you have to do is order by position

                PRIMARY KEY (user_id,ISBN),
                CONSTRAINT fk_library_queue_book FOREIGN KEY(ISBN) REFERENCES BOOKS(ISBN),
                CONSTRAINT fk_library_queue_user FOREIGN KEY(user_id) REFERENCES USERS(user_id)
            )
        """

        mycursor.execute(query1)
        mycursor.execute(query2)
        mycursor.execute(query3)


    # TODO clarify if we will account for the edge case when someone tries to check out the same book twice while first checkout period has not ended
    def book_checked_out(self, user_id, book_id, checkout_date = datetime.today().strftime('%Y-%m-%d')):
        try:
            query = f"""
                INSERT INTO LIBRARY_CHECKOUT (user_id, book_id, checkout_date)
                VALUES (%s, %s. %s)"""
            mycursor.execute(query, (user_id, book_id, checkout_date))
            mydb.commit()
        except mysql.connector.errors.IntegrityError as checkoutError:
            print(f"duplicateCheckout_error_already_checked_out: {checkoutError}")


    # Either provide the checkout_id and the return_date
    # Or provide user_id, book_id, checkout_date and the return_date
    def book_returned(self, checkout_id = None, user_id = None, book_id = None, checkout_date=None, return_date = datetime.today().strftime('%Y-%m-%d')):
        try:
            if checkout_id:
                query = f"""
                    UPDATE LIBRARY_CHECKOUT 
                    SET return_date = %s 
                    WHERE checkout_id = %s
                """
                mycursor.execute(query, (checkout_date, checkout_id))
                mydb.commit()
            elif user_id and book_id and checkout_date:
                query = f"""
                    UPDATE LIBRARY_CHECKOUT 
                    SET return_date = %s 
                    WHERE user_id = %s AND book_id = %s AND checkout_date = %s
                """
                mycursor.execute(query, (return_date, user_id, book_id, checkout_date))
                mydb.commit()
        except mysql.connector.errors as returnbookError:
            print(f"return_book_error: {returnbookError}")        

    # returns user checkout history for a given user
    # specifically: book_id, checkout_id, checkout_date, return_date, ISBN, name
    def get_user_checkout_history(self, user_id):
        assert user_id is not None, "provided None user_id" # idk if this is good python code style

        query =  f"""
            SELECT C.book_id, C.checkout_id, C.checkout_date, C.return_date, B.ISBN, B.name
            FROM LIBRARY_CHECKOUT C, BOOKS B
            WHERE C.user_id = %s 
            ORDER BY C.checkout_date DESC
        """
        
        mycursor.execute(query,(user_id,))
        result = mycursor.fetchall()

        return result


