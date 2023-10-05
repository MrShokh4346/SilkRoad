from flask import jsonify, request, redirect
from datetime import datetime, timedelta, timezone
from flask import Blueprint
from silk_road.api import bp 
from silk_road.models import *
from silk_road import jwt
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, create_refresh_token, get_jwt
from silk_road.serializers import *
from sqlalchemy.sql import func
from .utils import allowed_file
from werkzeug.utils import secure_filename
from flask import  send_from_directory, url_for, jsonify, request
from uuid import uuid1
from silk_road import UPLOAD_FOLDER
import os


@bp.route('/products', methods=['GET'])
def products():
    products = Product.query.all()
    data = []
    for product in products:
        d = product_schema.dump(product)
        d['rating'] = Comment.query.with_entities(func.avg(Comment.rating)).filter(Comment.product_id==product.id).all()[0][0] 
        data.append(d)
    return jsonify(data)


@bp.route('/product-by-subcategory')
def product_by_subcategory():
    subcategory_id = request.args.get('subcategory_id')
    products = Product.query.filter_by(subcategory_id=subcategory_id).all()
    data = []
    for product in products:
        d = product_schema.dump(product)
        d['rating'] = Comment.query.with_entities(func.avg(Comment.rating)).filter(Comment.product_id==product.id).all()[0][0] 
        data.append(d)
    return jsonify(data), 200


@bp.route('/product-by-id', methods=['GET'])
def product_by_id():
    product_id = request.args.get('product_id')
    product = product_by_id_schema.dump(db.get_or_404(Product, product_id))
    product['rating'] = Comment.query.with_entities(func.avg(Comment.rating)).filter(Comment.product_id==product_id).all()[0][0] 
    return jsonify(product)


@bp.route('/add-product', methods=['POST'])
@jwt_required()
def add_product():
    data = request.get_json()
    subcategory = Subcategory.query.get(data.get('subcategory_id'))
    product = Product(
        name = data.get('name'),
        material = data.get('material'),
        description = data.get('description'),
        care = data.get('care'),
        condition = data.get('condition'),
        design = data.get('design'),
        use = data.get('use'),
        discount = data.get('discount'),
        price = data.get('price'),
        old_price = data.get('old_price'),
        subcategory_id = data.get('subcategory_id')
    )
    db.session.add(product)
    db.session.commit()
    if data.get('size') is not None:
        for size in data.get('size'):
            sz = Size(deminsion=size, product_id=product.id)
            db.session.add(sz)
            db. session.commit()
    if data.get('weight') is not None:
        for wt in data.get('weight'):
            w = Weight(deminsion=wt, product_id=product.id)
            db.session.add(w)
            db.session.commit()
    if data.get('color') is not None:
        for cr in data.get('color'):
            c = Color(name=cr, product_id=product.id)
            db.session.add(c)
            db.session.commit()
    return jsonify(product_schema.dump(product))  


@bp.route('/product', methods=['PUT', 'PATCH', 'DELETE'])
@jwt_required()
def product():
    if request.method == 'PUT' or request.method == 'PATCH':
        data = request.get_json()
        product = db.get_or_404(Product, request.args.get('product_id'))
        product.name = data.get('name', product.name)
        product.material = data.get('material', product.material)
        product.description = data.get('description', product.description)
        product.care = data.get('care', product.care)
        product.condition = data.get('condition', product.condition)
        product.design = data.get('design', product.design)
        product.use = data.get('use', product.use)
        product.discount = data.get('discount', product.discount)
        product.price = data.get('price', product.price)
        product.old_price = data.get('old_price', product.old_price)
        product.subcategory_id = data.get('subcategory_id', product.subcategory_id)
        if data.get('size') is not None:
            old_s = Size.query.filter_by(product_id=product.id).all()
            for o_s in old_s:
                db.session.delete(o_s)
                db.session.commit()
            for size in data.get('size'):
                sz = Size(deminsion=size, product_id=product.id)
                db.session.add(sz)
                db. session.commit()
        if data.get('weight') is not None:
            old_w = Weight.query.filter_by(product_id=product.id).all()
            for o_w in old_w:
                db.session.delete(o_w)
                db.session.commit()
            for wt in data.get('weight'):
                w = Weight(deminsion=wt, product_id=product.id)
                db.session.add(w)
                db.session.commit()
        if data.get('color') is not None:
            old_c = Color.query.filter_by(product_id=product.id).all()
            for o_c in old_c:
                db.session.delete(o_c)
                db.session.commit()
            for cr in data.get('color'):
                c = Color(name=cr, product_id=product.id)
                db.session.add(c)
                db.session.commit()
        db.session.add(product)
        db.session.commit()
        return jsonify(product_by_id_schema.dump(product)), 200
    elif request.method == 'DELETE':
        product = db.get_or_404(Product, request.args.get('product_id'))
        db.session.delete(product)
        db.session.commit()
        return jsonify(msg="Product deleted")


@bp.route('/add-photo', methods=['POST'])
@jwt_required()
def add_photo():
    if 'photo' not in request.files:
        return jsonify({"msg":"No file part"})
    photo = request.files['photo']
    product_id = request.args.get('product_id')
    if photo.filename == '':
        return jsonify({'msg':'No file selected for uploading'})
    if photo and allowed_file(photo.filename):
        photoname = secure_filename(photo.filename)
        ft = photoname.rsplit('.', 1)[1].lower()
        photo_name = str(uuid1()) + '.' + ft
        ph = Photo(
            product_id = product_id,
            base = photo_name, 
        )
        db.session.add(ph)
        db.session.commit()
        photo.save(os.path.join(UPLOAD_FOLDER, photo_name))
        return jsonify(photo=ph.base)


@bp.route('/get-photo/<string:filename>')
def get_photo(filename):
    photo = Photo.query.filter_by(base=filename).first_or_404()
    return send_from_directory(f"../{UPLOAD_FOLDER}",filename)


@bp.route('/delete-photo/<string:filename>', methods=['DELETE'])
@jwt_required()
def delete_photo(filename):
    photo = Photo.query.filter_by(base=filename).first_or_404()
    os.remove(UPLOAD_FOLDER + filename)
    db.session.delete(photo)
    db.session.commit()
    return jsonify(msg="Deleted")
    

@bp.route('/comment/<product_id>', methods=['POST'])
def comment(product_id):
    product = db.get_or_404(Product, product_id)
    user = User.query.filter_by(email=request.get_json().get('email')).first()
    if user:
        comment = Comment(
            body = request.get_json().get('body'),
            product_id = product.id,
            user_id = user.id,
            author_email = user.email,
            rating = request.get_json().get('rating')
        )
    else:
        comment = Comment(
            body = request.get_json().get('body'),
            product_id = product.id,
            author_email = request.get_json().get('email'),
            rating = request.get_json().get('rating')
        )
    db.session.add(comment)
    db.session.commit()
    return jsonify(msg="Commented"), 200


@bp.route('/get-category')
def get_category():
    category = Category.query.all()
    return jsonify(category_schema.dump(category))


@bp.route('/get-subcategory')
def get_subcategory():
    subcategory = Subcategory.query.all()
    return jsonify(subcategory_schema.dump(subcategory))