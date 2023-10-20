from silk_road import jwt
from itsdangerous import URLSafeTimedSerializer
import string
import random
import os
from dotenv.main import load_dotenv
from silk_road import mail
from flask_mail import Message
from silk_road.models import BlacklistToken


load_dotenv()


def code_generator(size=6, chars=string.digits):
    return ''.join(random.choice(chars) for x in range(size))


# def send_email(email, code):
#     msg = Message(
#                 subject = "IT Club",
#                 body=f"Verification link - http://itclub21.pythonanywhere.com/auth/v1/{code}",
#                 sender='itclub79@gmail.com',
#                 recipients=[email])
#     mail.connect()
#     mail.send(msg)


def send_code(email, code):
    msg = Message(
                subject = "SilkRoute",
                body=f"Verification code - {code}",
                sender='itclub79@gmail.com',
                recipients=[email])
    mail.connect()
    mail.send(msg)


# def generate_token(email):
#     serializer = URLSafeTimedSerializer(os.environ["SECRET_KEY"])
#     return serializer.dumps(email, salt=os.environ["SECURITY_PASSWORD_SALT"])


# def confirm_token(token, expiration=3600):
#     serializer = URLSafeTimedSerializer(os.environ["SECRET_KEY"])
#     try:
#         email = serializer.loads(
#             token, salt=os.environ["SECURITY_PASSWORD_SALT"], max_age=expiration
#         )
#         return email
#     except Exception:
#         return False


# def generate_token_to_update_password(email):
#     serializer = URLSafeTimedSerializer(os.environ["SECRET_KEY"])
#     return serializer.dumps(email, salt=os.environ["SECURITY_PASSWORD_SALT"])


# def confirm_token_to_update_password(token, expiration=3600):
#     serializer = URLSafeTimedSerializer(os.environ["SECRET_KEY"])
#     try:
#         email = serializer.loads(
#             token, salt=os.environ["SECURITY_PASSWORD_SALT"], max_age=expiration
#         )
#         return email
#     except Exception:
#         return False


@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, decrypted_token):
    jti = decrypted_token['jti']
    token = BlacklistToken.query.filter_by(token=jti).first()
    return token is not None