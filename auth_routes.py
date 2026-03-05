from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from sqlalchemy.orm import Session
from dependecies import get_db, close_db
from model import User
from schemas import LoginSchema, UserSchema
from marshmallow import ValidationError
from main import login_manager
from werkzeug.security import check_password_hash, generate_password_hash

auth_router = Blueprint('auth', __name__, url_prefix='/auth')


def authenticate(email, password):
    db: Session = get_db()
    user = db.query(User).filter(User.email == email).first()
    
    if user and check_password_hash(user.password, password):
        return user
    return None

def create_token(user_id):
    return create_access_token(identity=str(user_id))

@auth_router.get("/")
async def home():
    return {"message": "Hello World! Auth Routes!"}

#Cadastar um usuário
@auth_router.post("/register")
async def register():

    db: Session = get_db()
    json_data = request.get_json()

    if not json_data:
        return jsonify({"error": "No input data provided"}), 400
    
    user_schema = UserSchema()

    try:
        data = user_schema.load(json_data)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_user = db.query(User).filter((User.email == data['email']) | (User.username == data['username'])).first()

    if new_user:
        return jsonify({"error": "Email or username already exists"}), 400
    else:
        hashed_password = generate_password_hash(data['password'])
        try:
            new_user = User(
                email=data['email'],
                username=data['username'],
                password=hashed_password
            )
            db.add(new_user)
            db.commit()
        except Exception as e:
            db.rollback()
            return jsonify({"error": str(e)}), 401
        finally:
            close_db()

    return {"message": "User registered successfully!"}

#Login de um usuário
@auth_router.post("/login")
async def login():

    db: Session = get_db()
    json_data = request.get_json()

    if not json_data:
        return jsonify({"error": "No input data provided"}), 400
    
    login_schema = LoginSchema()

    try:
        data = login_schema.load(json_data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    user = authenticate(data['email'], data['password'])
    if not user:
        return jsonify({"error": "Invalid email or password"}), 401
    else:
        access_token = create_token(user.id)
        return jsonify({"message": "Login successful!", "access_token": access_token}), 200