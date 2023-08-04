from CS157A.Database import mydb, mycursor
from CS157A.Database.Models.UserActivity import UserActivity

class BookRatings():

    def __init__(self) -> None:
        self.create_book_ratings_table()

    def create_book_ratings_table(self):
        query = f"""
            CREATE TABLE IF NOT EXISTS BOOK_RATING(
            user_id INTEGER NOT NULL,
            book_isbn VARCHAR(20) NOT NULL,
            rating_value ENUM('1', '2', '3', '4', '5') NOT NULL,
            CONSTRAINT book_rating FOREIGN KEY (user_id) REFERENCES USERS(user_id)
        );"""
        mycursor.execute(query)


    def add_rating(self, user_id: int, book_isbn: str, rating_value: int):
        query_check_existing_rating = f"""
            SELECT COUNT(*) FROM BOOK_RATING
            WHERE user_id=%s AND book_isbn=%s
        """
        mycursor.execute(query_check_existing_rating, (user_id, book_isbn))
        existing_rating_count = mycursor.fetchone()[0]

        if existing_rating_count == 0:
            query_insert_rating = f"""
                INSERT INTO BOOK_RATING(user_id, book_isbn, rating_value)
                VALUES (%s, %s, %s)
            """
            mycursor.execute(query_insert_rating, (user_id, book_isbn, rating_value))
            UserActivity().add_activity(user_id=user_id, activity_type="BOOK RATING", activity_msg=f"RATED BOOK: {book_isbn} | {rating_value} ☆")

        else:
            query_update_rating = f"""
                UPDATE BOOK_RATING
                SET rating_value=%s
                WHERE user_id=%s AND book_isbn=%s
            """
            mycursor.execute(query_update_rating, (rating_value, user_id, book_isbn))
            UserActivity().add_activity(user_id=user_id, activity_type="BOOK RATING", activity_msg=f"UPDATED RATING BOOK: {book_isbn} | {rating_value} ☆")

        mydb.commit()

    def get_specific_book_ratings_count(self, book_isbn:str, user_id:int):

        total_reviews_query = f"""
                SELECT COUNT(*) 
                FROM BOOK_RATING 
                WHERE book_isbn=%s        
            """
        mycursor.execute(total_reviews_query, (book_isbn, ))
        response = mycursor.fetchone()
        total_reviews = response[0]

        try:
            query = f"""
            SELECT rating_value
            FROM BOOK_RATING
            WHERE book_isbn=%s AND user_id=%s
            """
            mycursor.execute(query, (book_isbn, user_id))
            response = mycursor.fetchone()
            user_rating = response[0]
            return total_reviews, user_rating
        except:
           return total_reviews, 0

    def get_books_by_specific_rating(self, rating_value:int):
        query = f"""
            SELECT *
            FROM BOOK_RATING
            WHERE rating_value=%s
            ORDER BY rating_value DESC
        """
        mycursor.execute(query, (rating_value))
        response = mycursor.fetchall()
        columns = [col[0] for col in mycursor.description]
        dict_response = [dict(zip(columns, row)) for row in response]
        return dict_response
    
    def get_best_selling_books(self):
        query = f"""
            SELECT DISTINCT B.*, AVG(BR.rating_value) as avgRating, COUNT(BR.rating_value) as ratingCount
            FROM BOOKS B
            JOIN BOOK_RATING BR
                ON BR.book_isbn=B.ISBN
            GROUP BY B.ISBN
            ORDER BY avgRating DESC
            LIMIT 9
        """
        # Top 9 books only
        mycursor.execute(query, )
        response = mycursor.fetchall()
        columns = [col[0] for col in mycursor.description]
        dict_response = [dict(zip(columns, row)) for row in response]
        return dict_response
    
