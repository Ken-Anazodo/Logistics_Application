from flask import Blueprint

from ..jwt_auth import jwt

##creating an object for Blueprint and giving it a name
adminobj = Blueprint('bpadmin',__name__,template_folder='templates',static_folder='static',url_prefix='/admin')

##importing the route file from the admin folder
from . import admin_dashboard_api