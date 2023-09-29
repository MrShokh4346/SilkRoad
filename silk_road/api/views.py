from flask import jsonify, request, redirect
from datetime import datetime, timedelta, timezone
from flask import Blueprint
from silk_road.api import bp 
from silk_road.models import *
from silk_road import jwt
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, create_refresh_token, get_jwt
from silk_road.serializers import *
from sqlalchemy.sql import func


@bp.route('/products', methods=['GET', 'POST'])
def products():
    if request.method == 'GET':
        products = Product.query.all()
        data = []
        for product in products:
            d = product_schema.dump(product)
            d['rating'] = Comment.query.with_entities(func.avg(Comment.rating)).filter(Comment.product_id==product.id).all()[0][0] 
            data.append(d)
        return jsonify(data)
    elif request.method == 'POST':
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
        if data.get('photo') is not None:
            for ph in data.get('photo'):
                p = Photo(base=ph, product_id=product.id)
                db.session.add(p)
                db.session.commit()
        return jsonify(product_schema.dump(product))  


@bp.route('/product-by-subcategory')
def product_by_subcategory():
    subcategory_id = request.args.get('subcategory_id')
    products = Product.query.filter_by(subcategory_id=subcategory_id).all()
    data = []
    for product in products:
            d = product_schema.dump(product)
            d['rating'] = Comment.query.with_entities(func.avg(Comment.rating)).filter(Comment.product_id==product.id).all()[0][0] 
            data.append(d)
    return jsonify(data)


@bp.route('/product-by-id', methods=['GET', 'PUT', 'PATCH', 'DELETE'])
def product_by_id():
    if request.method == 'GET':
        product_id = request.args.get('product_id')
        product = product_by_id_schema.dump(db.get_or_404(Product, product_id))
        product['rating'] = Comment.query.with_entities(func.avg(Comment.rating)).filter(Comment.product_id==product_id).all()[0][0] 
        return jsonify(product)
    elif request.method == 'PUT' or request.method == 'PATCH':
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
        if data.get('photo') is not None:
            old_p = Photo.query.filter_by(product_id=product.id).all()
            for o_p in old_p:
                db.session.delete(o_p)
                db.session.commit()
            for ph in data.get('photo'):
                p = Photo(base=ph, product_id=product.id)
                db.session.add(p)
                db.session.commit()
        
        db.session.add(product)
        db.session.commit()
        return jsonify(product_by_id_schema.dump(product)), 200
    elif request.method == 'DELETE':
        product = db.get_or_404(Product, request.args.get('product_id'))
        db.session.delete(product)
        db.session.commit()
        return jsonify(msg="Product deleted")


@bp.route('/comment/<product_id>', methods=['POST'])
def comment(product_id):
    product = db.get_or_404(Product, product_id)
    user = User.query.filter_by(email=request.get_json().get('email')).first_or_404()
    comment = Comment(
        body = request.get_json().get('body'),
        product_id = product.id,
        user_id = user.id,
        author_name = user.first_name,
        rating = request.get_json().get('rating')
    )
    db.session.add(comment)
    db.session.commit()
    return jsonify(msg="Commented"), 200


@bp.route('/get-category')
def get_category():
    category = Category.query.all()
    print(category)
    return jsonify(category_schema.dump(category))


@bp.route('/get-subcategory')
def get_subcategory():
    subcategory = Subcategory.query.all()
    return jsonify(subcategory_schema.dump(subcategory))