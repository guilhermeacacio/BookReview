from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.orm import Session
from dependecies import get_db, close_db
from model import Book
from schemas import BookSchema
from marshmallow import ValidationError

book_router = Blueprint('book', __name__, url_prefix='/book')

@book_router.get("/")
async def home():
    return {"message": "Hello world! Book Routes!"}

#Register a new book
@book_router.post("/add_book")
@jwt_required() #Decorator to make the user athentication using the Token
async def add_book():

    db: Session = get_db() #Open the DB

    user_id = get_jwt_identity() #Check the user permission (if the user have the token the access will be allowed)

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    json_data = request.get_json()

    if not json_data:
        return {"error": "No input data provided"}, 400
    
    book_schema = BookSchema()

    try:
        data = book_schema.load(json_data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    try:
        new_book = Book(
            title=data['title'],
            author=data['author'],
            category=data.get('category')
        )
        db.add(new_book)
        db.commit()
        return jsonify({"message": "Book added successfully!"}), 201
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 401
    finally:
        close_db()

#Delete a book
@book_router.delete("/delete_book/<int:book_id>")
@jwt_required()
async def delete_book(book_id: int):

    db: Session = get_db()

    user_id = get_jwt_identity()

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    json_data = request.get_json()

    if not json_data:
        return {"error": "No input data provided"}, 400

    try:
        book = db.query(Book).filter(Book.id == book_id).first()
        if not book:
            return jsonify({"error": "Book not found"}), 404
        
        db.delete(book)
        db.commit()
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 401
    finally:
        close_db()

    return jsonify({"message": "Book deleted successfully!"}), 200 

#Update a book by ID
@book_router.put("/update_book/<int:book_id>")
@jwt_required()
async def update_book(book_id: int):

    db: Session = get_db()

    user_id = get_jwt_identity()

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    json_data = request.get_json()

    if not json_data:
        return jsonify({"error": "No input data provided"}), 400
    
    book_schema = BookSchema()

    try:
        data = book_schema.load(json_data)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    try:
        book = db.query(Book).filter(Book.id == book_id).first()
        if not book:
            return jsonify({"error": "Book not found"}), 404
        
        book.title = data['title']
        book.author = data['author']
        book.category = data.get('category', book.category)

        db.commit()
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 401
    finally:
        close_db()

    return jsonify({"message": f"Book with ID {book_id} updated successfully!"}), 200

#List a specific book (search a book by id)
@book_router.get("/get_book/<int:book_id>")
@jwt_required()
async def get_book(book_id):

    db: Session = get_db()

    user_id = get_jwt_identity()

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        book = db.query(Book).filter(Book.id == book_id).first()
        if not book:
            return jsonify({"error": "Book not found"}), 404
        
        book_schema = BookSchema()
        result = book_schema.dump(book)
    except Exception as e:
        return jsonify({"error": str(e)}), 401
    finally:
        close_db()

    return jsonify(result), 200

#List all the books
@book_router.get("/list_books")
@jwt_required()
async def list_books():

    db: Session = get_db()

    user_id = get_jwt_identity()

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        books = db.query(Book).all()
        book_schema = BookSchema(many=True)
        result = book_schema.dump(books)
    except Exception as e:
        return jsonify({"error": str(e)}), 401
    finally:
        close_db()
    return jsonify({
            "message": "List of all books retrieved successfully!", 
            "books": result

            }), 200
