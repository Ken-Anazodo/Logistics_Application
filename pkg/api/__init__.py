from flask import Blueprint

##creating an object for Blueprint and giving it a name
apiobj = Blueprint('bpapi',__name__,template_folder='templates',static_folder='static',url_prefix='/api')

##importing the route file from the admin folder
from . import api_route
