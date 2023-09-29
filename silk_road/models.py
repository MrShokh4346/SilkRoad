from silk_road import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import validates 
import re 
from datetime import datetime
from sqlalchemy.orm import backref

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password_hash = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, nullable=False)
    created = db.Column(db.DateTime, default=datetime.now())
    image = db.Column(db.Text)
    card = db.relationship('Card', backref=backref('user', passive_deletes=True), cascade='all, delete', lazy=True)
    comment = db.relationship('Comment', backref=backref('user', passive_deletes=True), cascade='all, delete', lazy=True)

    @property
    def password(self):
        raise AttributeError("Passwprd was unrreadable")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    @validates('email')
    def validate_email(self, key, email):
        if not re.match(r"^\S+@\S+\.\S+$", email):
            raise AssertionError('Email is incorrect')
        user = User.query.filter(User.email==email).first()
        if user:
            raise AssertionError('This email  alredy exist')
        return email

    @validates('phone')
    def validate_phone(self, key, phone):
        if phone[0] == '+':
            phone = phone.replace("+", "")
        if not re.match("^\\+?[1-9][0-9]{7,14}$", phone):
            raise AssertionError('Phone number is incorrect')
        user = User.query.filter(User.phone==phone).first()
        if user:
            raise AssertionError('This phone  alredy exist')
        return phone



class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    material = db.Column(db.String)
    size = db.relationship('Size', backref=backref('product', passive_deletes=True), cascade='all, delete', lazy=True)
    description = db.Column(db.String)
    color = db.relationship('Color', backref=backref('product', passive_deletes=True), cascade='all, delete', lazy=True)
    care = db.Column(db.String)
    condition = db.Column(db.String)
    discount = db.Column(db.Integer)
    design = db.Column(db.String)
    use = db.Column(db.String)
    weight = db.relationship('Weight', backref=backref('product', passive_deletes=True), cascade='all, delete', lazy=True)
    price = db.Column(db.Float)
    old_price = db.Column(db.Float)
    photo = db.relationship('Photo', backref=backref('product', passive_deletes=True), cascade='all, delete', lazy=True)
    subcategory_id = db.Column(db.Integer, db.ForeignKey("subcategory.id"))
    card = db.relationship('Card', backref=backref('product', passive_deletes=True), cascade='all, delete', lazy=True)
    wishlist = db.relationship('Wishlist', backref=backref('product', passive_deletes=True), cascade='all, delete', lazy=True)
    comment = db.relationship('Comment', backref=backref('product', passive_deletes=True), cascade='all, delete', lazy=True)


class Size(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    deminsion = db.Column(db.String)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"))
    card = db.relationship("Card", backref=backref('size'), lazy=True)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Integer)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id", ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete='CASCADE'), nullable=False)
    created = db.Column(db.DateTime, default=datetime.now())
    author_name = db.Column(db.String)
    rating = db.Column(db.Integer)


class Weight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    deminsion = db.Column(db.Text)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id", ondelete='CASCADE'), nullable=False)


class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    base = db.Column(db.String)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id", ondelete='CASCADE'), nullable=False)


class Color(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id", ondelete='CASCADE'), nullable=False)


class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id", ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete='CASCADE'), nullable=False)
    quantity = db.Column(db.Integer)
    size_id = db.Column(db.Integer, db.ForeignKey("size.id"), nullable=False)


class Wishlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id", ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete='CASCADE'), nullable=False)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    subcategory = db.relationship('Subcategory', backref=backref('category'), lazy=True)


class Subcategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    product = db.relationship('Product', backref=backref('subcategory'), lazy=True)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"))


class BlacklistToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    token = db.Column(db.String, nullable=False)
    blacklisted_on = db.Column(db.DateTime, nullable=False)