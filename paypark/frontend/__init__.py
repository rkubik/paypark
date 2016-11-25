# -*- coding: utf-8 -*-
from flask import Blueprint

frontend = Blueprint('frontend', __name__)

from . import account
from . import auth
from . import dashboard
from . import history
from . import license_plates
from . import phone_numbers
from . import session
