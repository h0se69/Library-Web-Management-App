from typing import Optional
from CS157A.Database import mydb, mycursor
import mysql.connector.errors
from datetime import datetime, timedelta


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

            checkout_date DATETIME NOT NULL,     -- DEFAULT NOW(),
            return_by DATETIME NOT NULL,         -- could be changed to a generate statement but no experience with them
            returned_date DATETIME DEFAULT NULL, -- this will keep track of if users returned books

            PRIMARY KEY (checkout_id),
            UNIQUE (user_id, book_id, checkout_date), -- user can check out same book multiple times
            CONSTRAINT fk_library_checkout_book FOREIGN KEY(book_id) REFERENCES LIBRARY_BOOKS(book_id),
            CONSTRAINT fk_library_checkout_user FOREIGN KEY(user_id) REFERENCES USERS(user_id)
        )
        """
        #TODO clarify if we want to give id to  late fees
        query2 = f"""CREATE TABLE IF NOT EXISTS {self.fines_table} (
            checkout_id INTEGER NOT NULL,
            amount DOUBLE NOT NULL,
            reason VARCHAR(512) NOT NULL, 
            paid BIT NOT NULL DEFAULT 0,

            PRIMARY KEY (checkout_id), -- might be wiser to have unique fineid because then user can be fined for late AND damaged books, 
                                       -- if no, it might be an option to combine checkout table and late fees table
            CONSTRAINT fk_library_fines_checkout_id FOREIGN KEY(checkout_id) REFERENCES LIBRARY_CHECKOUT(checkout_id)
        )
        """
        query3 = f"""CREATE TABLE IF NOT EXISTS LIBRARY_BOOK_QUEUE (
            user_id INT NOT NULL,
            ISBN VARCHAR(20) NOT NULL,
            position INT,
            PRIMARY KEY (user_id, position),
            UNIQUE (user_id, ISBN)
        );"""
        query4 = f"""CREATE TRIGGER before_queue_insert
            BEFORE INSERT ON LIBRARY_BOOK_QUEUE
            FOR EACH ROW
            BEGIN
                DECLARE max_position INT;
                SELECT COALESCE(MAX(position), 0) INTO max_position FROM LIBRARY_BOOK_QUEUE WHERE user_id = NEW.user_id;
                SET NEW.position = max_position + 1;
            END;"""

        mycursor.execute(query1)
        mycursor.execute(query2)
        mycursor.execute(query3)

        try:
            mycursor.execute(query4)
        except:
            print("Trigger duplicate")


    # Returns a list of avalable books for the provided ISBN
    def get_available_books(self, ISBN):
        query = f"""
            SELECT DISTINCT L.book_id
            FROM LIBRARY_BOOKS L
            WHERE L.ISBN = %s

            EXCEPT

            SELECT DISTINCT C.book_id
            FROM LIBRARY_CHECKOUT C
            WHERE C.returned_date IS NULL -- If it's null it's still checked out
        """
        #     EXCEPT 
        #
        #     SELECT DISTINCT C.book_id
        #     From LIBRARY_CHECKOUT C, LIBRARY_BOOKS L, LIBRARY_BOOK_QUEUE Q
        #     WHERE C.book_id = L.book_id AND L.ISBN = Q.ISBN  -- Also cannot check out directly if there is no one from queue who wants this book
        # """
        # TODO talk about how to handle the queue for placing hold on book and where to handle it, I am not sure if these should be excluded from the available books
        
        mycursor.execute(query,(ISBN,))
        result = mycursor.fetchall()

        return result

    def get_checkout_info(self, checkout_id):
        query = f"""
            SELECT * FROM LIBRARY_CHECKOUT
            WHERE checkout_id = %s
        """
        if checkout_id:
            mycursor.execute(query,(checkout_id,))
            result = mycursor.fetchall()
            return result
            

    # Given a user, book_id and a checkout date 
    # Will try to check out book from the library
    #
    # Returns True if the operation was a success, otherwise False
    def book_checked_out(self, user_id, book_id, return_by = (datetime.now() + timedelta(weeks=1)), checkout_date = datetime.now()):
        try:
            # if the book has no return date, that means it is already checked out
            check_occupied_query= f"""
                SELECT book_id, returned_date
                FROM LIBRARY_CHECKOUT
                WHERE returned_date IS NULL AND book_id = %s
            """
            mycursor.execute(check_occupied_query,(book_id,))
            occupied = mycursor.fetchall()

            # if the result is not empty then can't check out book,
            # otherwise the list is empty and you can check out book
            if occupied:
                print("Book is occupied")
                return False
            else:
                query = f"""
                    INSERT INTO LIBRARY_CHECKOUT (user_id, book_id, checkout_date, return_by)
                    VALUES (%s, %s, %s, %s)"""
                mycursor.execute(query, (user_id, book_id, checkout_date, return_by))
                mydb.commit()
                return True
        except mysql.connector.errors.IntegrityError as checkoutError:
            print(f"duplicateCheckout_error_book_checked_out: {checkoutError}")
            return False


    # Either provide the checkout_id and the return_date
    # Or provide user_id, book_id, checkout_date and the return_date
    # TODO make late returns automatically give a fine (add to LIBRARY_FINES) maybe add a field somewhere or a param to this func for fine value
    def book_returned(self, checkout_id = None, user_id = None, book_id = None, return_date = datetime.now()):
        try:
            #print(f"cid: {checkout_id} \nuser_id: {user_id} \nbook_id: {book_id} \nreturned_date: {return_date}")
            if checkout_id:
                query = f"""
                    UPDATE LIBRARY_CHECKOUT 
                    SET returned_date = %s 
                    WHERE checkout_id = %s
                """
                mycursor.execute(query, (return_date, checkout_id))
                mydb.commit()
                return True
            elif user_id and book_id:
                query = f"""
                    UPDATE LIBRARY_CHECKOUT 
                    SET returned_date = %s 
                    WHERE user_id = %s AND book_id = %s AND returned_date IS NULL
                """
                mycursor.execute(query, (return_date, user_id, book_id))
                mydb.commit()
                return True
            else: 
                return False
        except mysql.connector.errors as returnbookError:
            print(f"return_book_error: {returnbookError}")
            return False        


    # returns user checkout history for a given user
    # specifically: book_id, checkout_id, checkout_date, return_date, ISBN, name
    def get_user_checkout_history(self, user_id):
        assert user_id is not None, "provided None user_id" # idk if this is good python code style

        # if the book name is unecessary then it can be easily be removed later
        query =  f"""
            SELECT C.book_id, C.checkout_id, C.checkout_date, C.return_date, B.ISBN, B.name
            FROM LIBRARY_CHECKOUT C, LIBRARY_BOOKS L, BOOKS B
            WHERE C.user_id = %s AND C.book_id = L.book_id AND L.ISBN = B.ISBN
            ORDER BY C.checkout_date DESC
        """
        
        mycursor.execute(query,(user_id,))
        result = mycursor.fetchall()

        return result


    def add_user_to_waiting_list(self, user_id, ISBN):
        try:
            query = f"""
            INSERT INTO LIBRARY_BOOK_QUEUE (user_id, ISBN)
            VALUES (%s , %s);"""
            mycursor.execute(query, (user_id,ISBN))
            mydb.commit()
        except mysql.connector.errors.IntegrityError as duplicateHold:
            print(f"duplicateHold_Error_add_user_to_waiting_list: {duplicateHold}")


    # Can either provide checkout_id, or 
    # user_id, book_id (will assume most recent checkout of the book by the user)
    # 
    # will add default fine of 5.01$ with reason default reason late return
    def add_fee(self, checkout_id = None, user_id = None, book_id = None, amount = 5.01, reason_s = "late return"):
        if not checkout_id:
            checkout_search = f"""SELECT checkout_id 
                FROM LIBRARY_CHECKOUT 
                WHERE user_id = %s AND book_id = %s -- will assume most recent one
                ORDER BY returned_date DESC, returned_date IS NULL -- if still checked out will grab that book
                LIMIT 1
            """
            mycursor.execute(checkout_search,(user_id,book_id))
            checkout_search_result = mycursor.fetchall()
            if len(checkout_search_result) != 0:
                checkout_id = checkout_search_result[0][0] # get the first result of the first tuple

        query = f"""
            INSERT INTO LIBRARY_FINES (checkout_id, amount, reason)
            VALUES (%s,%s,%s);
        """
        if checkout_id:
            try:
                mycursor.execute(query, (checkout_id, amount, reason_s))
                mydb.commit()
                return True
            except mysql.connector.errors.IntegrityError as duplicateFine:
                print(f"duplicateFine_Error_add_fee: {duplicateFine}")
                return False
        else:
            return False

    def resolve_fee(self,checkout_id, user_id, book_id, checkout_date):
        if not checkout_id:
            checkout_search = f"""SELECT checkout_id 
                FROM LIBRARY_CHECKOUT 
                WHERE user_id = %s AND book_id = %s AND checkout_date = %s
            """
            mycursor.execute(checkout_search,(user_id,book_id,checkout_date))
            checkout_search_result = mycursor.fetchall()
            if len(checkout_search_result) != 0:
                checkout_id = checkout_search_result[0][0] # get the first result of the first tuple

        query = f"""
            UPDATE LIBRARY_FINES 
            SET paid = 1 
            WHERE checkout_id = %s;
        """
        if checkout_id: 
            try:
                mycursor.execute(query, (checkout_id,))
                mydb.commit()
            except mysql.connector.errors.IntegrityError as Fine:
                print(f"Fine_Error_resolve_fee: {Fine}")

    def is_book_checked_out(self, book_id):
        check_occupied_query= f"""
            SELECT book_id, returned_date
            FROM LIBRARY_CHECKOUT
            WHERE returned_date IS NULL AND book_id = %s
        """
        mycursor.execute(check_occupied_query,(book_id,))
        occupied = mycursor.fetchall()

        if occupied:
            return False
        else:
            return True
        
    def is_same_checkout_user(self, user_id:int, book_id):
        query = f"""
            SELECT *
            FROM LIBRARY_CHECKOUT
            WHERE user_id = %s AND book_id = %s
        """
        mycursor.execute(query, (user_id, book_id))
        isSame = mycursor.fetchall()

        if isSame:
            return True
        else:
            return False