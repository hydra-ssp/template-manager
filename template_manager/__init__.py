from flask import Blueprint

templatemanager = Blueprint('template_manager', __name__,
                       template_folder='templates',
                       static_folder='static/template_manager',
                       static_url_path='/templates/static')

from .views import *
