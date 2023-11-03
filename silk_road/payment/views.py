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

    customer = stripe.Customer.create(
        email=user.email,
        name=user.first_name,
        phone=user.phone
    )
    order = Order(
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
    return jsonify(order_id=order.id)


@bp.route('/payment-method', methods=['POST'])
def payment():
    data = request.get_json()
    order = db.get_or_404(Order, data.get('order_id'))
    stripe.PaymentMethod.attach(
            data.get("payment_method"),
            customer=order.customer_id
        )
    payment_intent = stripe.PaymentIntent.create(
        amount=order.total_price,  
        currency="usd",
        payment_method=data.get("payment_method"),
        customer=order.customer_id,
        setup_future_usage="off_session",
        confirm=True,
        payment_method_types=["card"],
        description="Payment for multiple products",
    )
    order.payment_intent_id = payment_intent.id
    db.session.commit()
    return jsonify(msg="Ok")


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
        payment_intent = event.data.object
        order = Order.query.filter_by(payment_intent_id=payment_intent.id).first()
        order.payed = True
        db.session.commit()
        print("payment_intent.succeeded")
        return jsonify(msg="Payment was succesfull")
    elif event.type == 'payment_method.attached':
        payment_method = event.data.object # contains a stripe.PaymentMethod
        
        # Then define and call a method to handle the successful attachment of a PaymentMethod.
        # handle_payment_method_attached(payment_method)
        # ... handle other event types
        print("payment_intent.attached")

    else:
        print('Unhandled event type {}'.format(event.type))

    return jsonify(msg="success")