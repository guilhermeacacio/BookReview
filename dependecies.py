from model import db, User
from flask import g
from sqlalchemy.orm import Session, sessionmaker

Session = sessionmaker(bind=db)

def get_db():
    if 'db_session' not in g:
        g.db_session = Session()
    
    return g.db_session

def close_db(e=None):
    db_session = g.pop('db_session', None)

    if db_session is not None:
        db_session.close()

def verify_token(token):
    # Implement your token verification logic here
    # For example, you can decode the token and check its validity
    pass