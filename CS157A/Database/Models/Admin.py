import os
import bcrypt
from CS157A.Database import mydb, mycursor

class Admin():

    def __init__(self) -> None:
        self.create_admin_table()
        self.authorize_default_admins()

    def create_admin_table(self):
        query = f"""
            CREATE TABLE IF NOT EXISTS ADMIN_USERS(
            user_id INTEGER PRIMARY KEY AUTO_INCREMENT,
            email VARCHAR(255) NOT NULL UNIQUE,
            first_name VARCHAR(255) NOT NULL,
            last_name VARCHAR(255) NOT NULL,
            password VARCHAR(255) NOT NULL
        );"""
        mycursor.execute(query)

    def authorize_default_admins(self):
        email = "admin_user@cs157a.com"
        first_name = "cs157A"
        last_name = "admin"
        password = "password"

        query = f"""
            INSERT INTO ADMIN_USERS(email, first_name, last_name, password)
            VALUES('{email}', '{first_name}', '{last_name}', '{password}')
        """
        mycursor.execute(query)
        mydb.commit()

    def add_admin(self, email:str, first_name:str, last_name:str, password:str):
        query = f"""
            INSERT INTO ADMIN_USERS(email, first_name, last_name, password)
            VALUES('{email}', '{first_name}', '{last_name}', '{password}')
        """
        mycursor.execute(query)
        mydb.commit()

    def remove_admin(self, email:str):
        query = f"""
            REMOVE FROM ADMIN_USERS 
            WHERE email='{email}'
        """
        mycursor.execute(query)
        mydb.commit()

    def check_is_admin(self, email:str, password:str):
        password = password.encode('utf-8')
        query = f"""
                SELECT password
                FROM ADMIN_USERS
                WHERE email='{email}'
                """
        mycursor.execute(query)
        response_password = mycursor.fetchone()

        if(response_password):
            hashed_response_password = str(response_password[0]).encode('utf-8')
            decoded_hashed_password = hashed_response_password.decode("utf-8")
            is_same_password = bcrypt.checkpw(password, hashed_response_password)
            
            if(is_same_password):
                query = f"""
                    SELECT AU.first_name, AU.email, AU.user_id
                    FROM ADMIN_USERS AU
                    WHERE AU.email='{email}' AND AU.password='{decoded_hashed_password}'
                    """
                mycursor.execute(query)
                response = mycursor.fetchone()
                if(response):
                    first_name = response[0]
                    email = response[1]
                    user_id = response[2]
                    return first_name, email, user_id
                else:
                    return False
            else:
                return False
        else:
            return False