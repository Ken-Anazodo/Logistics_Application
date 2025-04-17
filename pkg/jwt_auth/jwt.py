import jwt
import datetime
from flask import url_for
from flask_jwt_extended import JWTManager, create_access_token
from flask import current_app #Flask provides current_app, which lets you access the app instance without directly importing it(to avoid the circular import), instead of "from pkg import app". another alternative is to import app iside a function like the below 
from pkg.models import Administrator



def create_jwt_token(id):
    access_token = create_access_token(identity=str(id))
    return access_token


def generate_admin_verification_token(email):
    # from pkg import app #(to avoid circular import)
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    payload = {
        "email": email,
        "exp": expiration_time
    }

    jwt_key = current_app.config['JWT_SECRET_KEY']
    token = jwt.encode(payload, jwt_key, algorithm="HS256")
    return token


def generate_admin_verification_link(token):
    return url_for("bpadmin.verify_admin_email", token=token, _external=True)




