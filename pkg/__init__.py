import os
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from flask_mail import Mail
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv


load_dotenv()
mail=Mail()
csrf = CSRFProtect()
jwt = JWTManager()

def create_app():
    from pkg.models import db
    from pkg import config

    ## bring in the instamces of the blueprints
    from pkg.admin import adminobj
    from pkg.user import userobj
    from pkg.api import apiobj

    ##create instance of an object of flask
    app = Flask(__name__,instance_relative_config=True)

    ## register the blueprints with app so that our flask app can be aware of them
    
    app.register_blueprint(apiobj)
    app.register_blueprint(userobj)
    app.register_blueprint(adminobj)
    
   

    ## load your config before initializing db
    app.config.from_pyfile('config.py',silent=True)
    app.config.from_object(config.LiveConfig)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'fallback-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
    app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL') == 'True'
    
    ## wrap your flask app with the various instance so that they would be available globally
    db.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)
    jwt.init_app(app)
    CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}}, supports_credentials=True)


    ##removing csrf protection from the routes in api package
    csrf.exempt(apiobj)
    csrf.exempt(adminobj)

    migrate = Migrate(app,db)
    
    return app

app = create_app()

from pkg import models,forms,general_route