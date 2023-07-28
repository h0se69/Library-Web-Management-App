import os
import bcrypt
from CS157A.Database import mydb, mycursor
import datetime


class UserActivity():

    def __init__(self) -> None:
        self.create_activity_table()

    def create_activity_table(self):
        query = f"""
            CREATE TABLE IF NOT EXISTS USER_ACTIVITY(
            user_id INTEGER NOT NULL,
            activity_type VARCHAR(100) NOT NULL,
            activity_msg VARCHAR(255) NOT NULL,
            activity_timestamp TIMESTAMP  NOT NULL,
            CONSTRAINT user_activity_fk FOREIGN KEY (user_id) REFERENCES USERS(user_id)
        );"""
        mycursor.execute(query)

    def add_activity(self, user_id:int, activity_type:str, activity_msg:str):
        activity_timestamp = datetime.datetime.now()
        query = f"""
            INSERT INTO USER_ACTIVITY(user_id, activity_type, activity_msg, activity_timestamp)
            VALUES (%s, %s, %s, %s)
        """
        mycursor.execute(query, (user_id, activity_type, activity_msg, activity_timestamp))
        mydb.commit()

    def get_all_activities(self, user_id:int):
        query = f"""
            SELECT *
            FROM USER_ACTIVITY
            WHERE user_id={user_id}
            ORDER BY activity_timestamp DESC
        """
        mycursor.execute(query, )
        response = mycursor.fetchall()
        columns = [col[0] for col in mycursor.description]
        dict_response = [dict(zip(columns, row)) for row in response]
        return dict_response