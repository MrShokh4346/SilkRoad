from flask import jsonify, request, redirect
from datetime import datetime, timedelta, timezone
from flask import Blueprint
from silk_road.payment import bp
from silk_road.models import *
from silk_road import jwt
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, create_refresh_token, get_jwt
from silk_road.serializers import *
import stripe


@bp.route('/orders', methods=['POST'])
@jwt_required()
def orders():
    id = get_jwt_identity()
    user = db.get_or_404(User, id)
    data = request.get_json()
    total_price = 0

    line_items = []

    customer = stripe.Customer.create(
        email=user.email,
        name=user.first_name,
        phone=user.phone
    )
    order = Orders(
            customer_id = customer.id
        )
    db.session.add(order)
    db.session.commit()

    for product in data.get('products'):
        pd = db.get_or_404(Product, product['product_id'])

        p = stripe.Product.create(
            name=pd.name,
            description=pd.description
        )

        unit_amount = (pd.price if pd.price else pd.old_price) * 100
        total_price += unit_amount

        price = stripe.Price.create(
            product=p.id,
            unit_amount=unit_amount, 
            currency="gbp"
        )

        line_items.append({
            'price':price.id,
            'quantity':product.get('quantity')
        })

        card = Card(
            product_id = product.get('product_id'),
            user_id = id,
            quantity = product.get('quantity'),
            color = product.get('color'),
            size = product.get('size'),
            order_id = order.id
        )
        db.session.add(card)

    if data.get('destination'):
        order.destination = data.get('destination')
    order.total_price=total_price
    db.session.commit()
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=line_items,
            mode='payment',
            currency='gbp',
            customer=customer,
            success_url="http://silkroaditc21.pythonanywhere.com/payment/v1/success",
            cancel_url="http://silkroaditc21.pythonanywhere.com/payment/v1/fail",
            )
    except Exception as e:
        return str(e)
    return jsonify(checkout_session.url)


@bp.route('/success')
def success():
    return jsonify(msg="Success")


@bp.route('/fail')
def fail():
    return jsonify(msg="Fail")


@bp.route('/webhook', methods=['POST'])
def webhook():
    payload = request.get_json()
    event = None
    try:
        event = stripe.Event.construct_from(
            payload, stripe.api_key
        )
    except ValueError as e:
        # Invalid payload
        return jsonify(msg=f"{e}")

    # Handle the event
    if event.type == 'payment_intent.succeeded':
        payment_intend = event.data.object
        order = Orders.query.filter_by(customer_id=payment_intend.customer).first()
        order.payed = True
        db.session.commit()
        print("payment_intent.succeeded")
        return jsonify(msg="Payment was succesfull")
    else:
        print('Unhandled event type {}'.format(event.type))

    return jsonify(msg="success")