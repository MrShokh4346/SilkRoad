from flask import jsonify, request, redirect
from datetime import datetime, timedelta, timezone
from flask import Blueprint
from silk_road.api import bp 
from silk_road.models import *
from silk_road import jwt
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, create_refresh_token, get_jwt
from silk_road.serializers import *


@bp.route('/products', methods=['GET', 'POST'])
def products():
    if request.method == 'GET':
        products = Product.query.all()
        return jsonify(product_schemas.dump(products))
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
            score = data.get('score'),
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
    products = Product.query.filter_by(subcategory_id=subcategory_id)
    return jsonify(product_schemas.dump(products))


@bp.route('/get-category')
def get_category():
    category = Category.query.all()
    print(category)
    return jsonify(category_schema.dump(category))


@bp.route('/get-subcategory')
def get_subcategory():
    subcategory = Subcategory.query.all()
    return jsonify(subcategory_schema.dump(subcategory))