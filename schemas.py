from flask_marshmallow import Marshmallow
from marshmallow import Schema, fields, post_load

ma = Marshmallow()

class UserSchema(ma.Schema):
    email = fields.Str(required=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)
    admin = fields.Bool(load_default=False)
    
class AuthorSchema(ma.Schema):
    name = fields.Str(required=True)

class ReviewSchema(ma.Schema):
    rating = fields.Float(required=True)
    comment = fields.Str()
    book_id = fields.Int(required=True)
    user_id = fields.Int(required=True)

class BookSchema(ma.Schema):
    title = fields.Str(required=True)
    author = fields.Str(required=True)
    category = fields.Str()
    average_rating = fields.Float(dump_only=True)
    
class CategorySchema(ma.Schema):
    name = fields.Str(required=True)

class LoginSchema(ma.Schema):
    email = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)