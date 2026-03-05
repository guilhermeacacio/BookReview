from datetime import timedelta
from flask import Flask
from flask_login import LoginManager
from dotenv import load_dotenv
import os
from flask_jwt_extended import JWTManager
from dependecies import close_db

load_dotenv()

#Get the authenticate values saved in .env file and save in a variables
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

app = Flask(__name__)  

#Guarantee that the db always close after a route finish
app.teardown_appcontext(close_db)

#Configurate the authenticate using Flask JWT
app.config["JWT_SECRET_KEY"] = os.getenv("SECRET_KEY") 
app.config["JWT_ALGORITHM"] = os.getenv("ALGORITHM", "HS256")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)))

jwt = JWTManager(app)

login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

@app.route('/')
def hello_world():
    return 'Hello, World!'

from auth_routes import auth_router
from books_routes import book_router

app.register_blueprint(auth_router)
app.register_blueprint(book_router)