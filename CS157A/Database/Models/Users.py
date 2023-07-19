import os
import bcrypt
from CS157A.Database import mydb, mycursor


class Users():
    def __init__(self) -> None:
        self.salt_value = bcrypt.gensalt(12, b'2a')
        self.create_user_table()

    def create_user_table(self):
        query = f"""
            CREATE TABLE IF NOT EXISTS Users(
            user_id INTEGER PRIMARY KEY AUTO_INCREMENT,
            email VARCHAR(255) NOT NULL,
            first_name VARCHAR(255) NOT NULL,
            last_name VARCHAR(255) NOT NULL,
            password VARCHAR(255) NOT NULL
        );"""
        mycursor.execute(query)

    def register_user(self, email:str, first_name:str, last_name:str, password:str):
        encoded_password = str(password).encode('utf-8')
        hashed_password = bcrypt.hashpw(password=encoded_password, salt=self.salt_value)
        decoded_hashed_password = hashed_password.decode('utf-8') # removes the binary tag

        does_email_exist = self.check_user_email(email)
        if(does_email_exist):
            return f"{email} already registered..."
        else:
            self.store_register_user_data(email=email, first_name=first_name, last_name=last_name, password=decoded_hashed_password)
            return True

    def store_register_user_data(self, email:str, first_name:str, last_name:str, password:str):
        query = f"""
        INSERT INTO Users(email, first_name, last_name, password)
        VALUES('{email}', '{first_name}', '{last_name}', '{password}')
        """
        mycursor.execute(query)
        mydb.commit()

    def check_user_email(self, email:str):
        query = f"""
                SELECT COUNT(*)
                FROM Users
                WHERE Users.email='{email}'
                """
        mycursor.execute(query)
        response = mycursor.fetchone()
        if response:
            count = response[0]
            if(count >= 1):
                return True # already exists

    def authenticate_user(self, email:str, password:str):
        password = password.encode('utf-8')
        query = f"""
                SELECT U.password
                FROM Users U
                WHERE U.email='{email}'
                """
        mycursor.execute(query)
        response_password = mycursor.fetchone()

        if(response_password):
            hashed_response_password = str(response_password[0]).encode('utf-8')
            decoded_hashed_password = hashed_response_password.decode("utf-8")
            is_same_password = bcrypt.checkpw(password, hashed_response_password)
            
            if(is_same_password):
                query = f"""
                    SELECT U.first_name, U.email, U.user_id
                    FROM Users U
                    WHERE U.email='{email}' AND U.password='{decoded_hashed_password}'
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
        
    def get_user_information(self, user_id:int, email:str):
        query = f"""
            SELECT U.user_id, U.first_name, U.last_name, U.email
            FROM Users U
            WHERE U.user_id={user_id} AND U.email='{email}'
            """
        mycursor.execute(query)
        response = mycursor.fetchone()
        if(response):
            user_id = response[0]
            first_name = response[1]
            last_name = response[2]
            email = response[3]
        
            return {
                "user_id" : user_id,
                "first_name" : first_name,
                "last_name" : last_name,
                "email" : email
            }
        else:
            return None