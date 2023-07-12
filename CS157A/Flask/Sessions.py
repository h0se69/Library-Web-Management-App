from functools import wraps
from typing import Optional
from flask import session

def set_user_session(email:str, first_name:str, user_id: int):
    session['authenticated'] = True
    session['email'] = email
    session['first_name'] = first_name
    session['user_id'] = user_id
    return session
