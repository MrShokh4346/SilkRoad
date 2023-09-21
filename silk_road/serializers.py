from marshmallow import Schema, validates, fields, post_load
from silk_road.models import *
import re


class UserSerializer(Schema):
    id = fields.Integer(dump_only=True)
    first_name = fields.String(required=True)
    last_name = fields.String()
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True)
    phone = fields.String(required=True)
    created = fields.DateTime(dump_only=True)
    image = fields.String()

    @post_load
    def make_object(self, data, **kwargs):
        return User(**data)

    @validates('email')
    def validate_email(self, email):
        if not re.match(r"^\S+@\S+\.\S+$", email):
            raise AssertionError('Email is incorrect')
        user = User.query.filter(User.email==email).first()
        if user:
            raise AssertionError('This email  alredy exist')
        return email

    @validates('phone')
    def validate_phone(self, phone):
        if not re.match("^\\+?[1-9][0-9]{7,14}$", phone):
            raise AssertionError('Phone number is incorrect')
        return phone

user_schema = UserSerializer()


class ProductSerializer(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String
    material = fields.String
    size = fields.String
    description = fields.String
    color = fields.String
    care = fields.String
    condition = fields.String
    design = fields.String
    use = fields.String
    weight = db.Column(db.Integer)
    price = db.Column(db.Integer)
    old_price = db.Column(db.Integer)
    photo = db.Column(db.Integer)
    score = db.Column(db.Integer)
    subcategory_id = db.Column(db.Integer, db.ForeignKey("subcategory.id"))




# class CategorySerializer(Schema):
#     id = fields.Integer(dump_only=True)
#     category = fields.String(dump_only=True)
#     icon = fields.String(dump_only=True)
#     subcategory = fields.Nested(SubCategorySerializer, dump_only=True, many=True)
