from flask_login import UserMixin
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float, ForeignKey, select, func
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.ext.hybrid import hybrid_property

db = create_engine('sqlite:///app.db')
Base = declarative_base()

class User(Base, UserMixin):
    __tablename__ = 'users'
    id = Column('id', Integer, primary_key=True)
    email = Column('email',String, unique=True, nullable=False)
    username = Column('username',String, unique=True, nullable=False)
    password = Column('password', String, nullable=False)
    admin = Column('admin',Boolean, default=False)

    reviews = relationship("Review", back_populates="user")

    def __init__(self, email, username, password, admin=0):
        self.email = email
        self.username = username
        self.password = password
        self.admin = admin


class Review(Base):
    __tablename__ = 'reviews'
    id = Column('id', Integer, primary_key=True)
    rating = Column('rating', Float, nullable=False)  # Rating given by the user
    comment = Column('comment', String, default='')  # Comment about the book
    book_id = Column('book_id', Integer, ForeignKey('books.id'), nullable=False)  # Foreign key to associate review with a book
    user_id = Column('user_id', Integer, ForeignKey('users.id'), nullable=False)  # Foreign key to associate review with a user

    book = relationship("Book", back_populates="reviews")
    user = relationship("User", back_populates="reviews")

    def __init__(self, rating, book_id, user_id, comment='',):
        self.rating = rating
        self.comment = comment
        self.book_id = book_id
        self.user_id = user_id

class Book(Base):
    __tablename__ = 'books'
    id = Column('id', Integer, primary_key=True)
    title = Column('title', String, nullable=False)
    author = Column('author', String, nullable=False)
    category = Column('category', String, default='')  # Category of the book
    
    reviews = relationship("Review", back_populates="book")

    def __init__(self, title, author, category=''):
        self.title = title
        self.author = author
        self.category = category

    @hybrid_property
    def average_rating(self):
        if self.reviews:
            return sum(r.rating for r in self.reviews) / len(self.reviews)
        return 0

    # Isso aqui permite que o Banco de Dados faça o cálculo rápido
    @average_rating.expression
    def average_rating(cls):
        return (
            select(func.avg(Review.rating))
            .where(Review.book_id == cls.id)
            .label("average_rating")
        )

Base.metadata.create_all(db)