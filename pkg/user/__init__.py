from flask import Blueprint

##creating an object for Blueprint and giving it a name
userobj = Blueprint('bpuser',__name__,template_folder='templates',static_folder='static',url_prefix='/user')

##importing the route file from the admin folder
from . import user_route