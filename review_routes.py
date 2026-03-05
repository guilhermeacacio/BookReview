from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from marshmallow import ValidationError
from sqlalchemy.orm import Session
from dependecies import get_db, close_db
from model import Review
from schemas import ReviewSchema

review_router = Blueprint('review', __name__, url_prefix='/review')

@review_router.get("/")
async def home():
    return {"message": "Hello world! Review Routes!"}

#gerar uma rota para adicionar um review
@review_router.post("/add_review")
@jwt_required()
async def add_review():

    db: Session = get_db()

    user_id = get_jwt_identity()

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    json_data = request.get_json()

    if not json_data:
        return {"error": "No input data provided"}, 400
   
    review_schema = ReviewSchema()

    try:
        data = review_schema.load(json_data)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    try:
        new_review = Review(
            book_id=data['book_id'],
            user_id=user_id,
            rating=data['rating'],
            comment=data.get('comment')
        )
        db.add(new_review)
        db.commit()
        return jsonify({"message": "Review added successfully!"}), 201
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 401
    finally:
        close_db()
    

#gerar uma rota para atualizar um review
@review_router.put("/update_review/<int:review_id>")
@jwt_required()
async def update_review(review_id: int):

    db: Session = get_db()

    user_id = get_jwt_identity()

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    json_data = request.get_json()

    if not json_data:
        return jsonify({"error": "No input data provided"}), 400
   
    review_schema = ReviewSchema()

    try:
        data = review_schema.load(json_data)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    try:
        review = db.query(Review).filter(Review.id == review_id, Review.user_id == user_id).first()
        
        if not review:
            return jsonify({"error": "Review not found or unauthorized"}), 404
        
        review.rating = data['rating']
        review.comment = data.get('comment', review.comment)
        
        db.commit()
        return jsonify({"message": "Review updated successfully!"}), 200
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 401
    finally:
        close_db()

#gerar uma rota para deletar um review
@review_router.delete("/delete_review/<int:review_id>")
@jwt_required()
async def delete_review(review_id: int):

    db: Session = get_db()

    user_id = get_jwt_identity()

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    json_data = request.get_json()

    if not json_data:
        return jsonify({"error": "No input data provided"}), 400
    
    try:
        review = db.query(Review).filter(Review.id == review_id).first()

        if not review:
            return jsonify({"error": "Review not found"}), 404
        
        db.delete(review)
        db.commit()
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 401
    finally:
        close_db()
    
    return jsonify({"message": "Review deleted successfully!"}), 200
