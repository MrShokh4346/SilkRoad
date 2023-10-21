from marshmallow import Schema, validates, fields, post_load
from silk_road.models import *
import re


class ProfilePhotoSerializer(Schema):
    id = fields.Integer(dump_only=True)
    base = fields.String(required=True)


class UserSerializer(Schema):
    id = fields.Integer(dump_only=True)
    first_name = fields.String(required=True)
    last_name = fields.String()
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True)
    phone = fields.String(required=True)
    created = fields.DateTime(dump_only=True)
    photo = fields.Nested(ProfilePhotoSerializer, dump_only=True, required=True, many=True)


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


class CategorySerializer(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)

category_schema = CategorySerializer()
categories_schema = CategorySerializer(many=True)



class SubcategorySerializer(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)

subcategory_schema = SubcategorySerializer()
subcategories_schema = SubcategorySerializer(many=True)



class WeightSerializer(Schema):
    id = fields.Integer(dump_only=True)
    deminsion = fields.String(required=True)


class PhotoSerializer(Schema):
    id = fields.Integer(dump_only=True)
    base = fields.String(required=True)


class ColorSerializer(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)


class SizeSerializer(Schema):
    id = fields.Integer(dump_only=True)
    deminsion = fields.String(required=True)

size_schema = SizeSerializer()


class CommentSerialize(Schema):
    id = fields.Integer(dump_only=True)
    body = fields.String(required=True)
    author_email = fields.String(required=True)
    created = fields.DateTime(dump_only=True)
    rating = fields.Integer(required=True)


class ProductByIdSerializer(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    material = fields.String()
    description = fields.String(required=True)
    care = fields.String()
    condition = fields.String()
    design = fields.String()
    discount = fields.Integer()
    use = fields.String()
    price = fields.Integer(required=True)
    old_price = fields.Integer()
    score = fields.Integer(required=True)
    subcategory = fields.Nested(SubcategorySerializer, dump_only=True, required=True)
    comment = fields.Nested(CommentSerialize, dump_only=True, required=True, many=True)
    weight = fields.Nested(WeightSerializer, dump_only=True, required=True, many=True)
    photo = fields.Nested(PhotoSerializer, dump_only=True, required=True, many=True)
    size = fields.Nested(SizeSerializer, dump_only=True, required=True, many=True)
    color = fields.Nested(ColorSerializer, dump_only=True, required=True, many=True)

product_by_id_schema = ProductByIdSerializer()


class ProductSerializer(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    discount = fields.Integer()
    price = fields.Integer(required=True)
    old_price = fields.Integer()
    score = fields.Integer(required=True)
    subcategory = fields.Nested(SubcategorySerializer, dump_only=True, required=True)
    photo = fields.Nested(PhotoSerializer, dump_only=True, required=True, many=True)

product_schemas = ProductSerializer(many=True)
product_schema = ProductSerializer()


