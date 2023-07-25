from typing import Optional
from CS157A.Database import mydb, mycursor
import mysql.connector.errors


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


        
