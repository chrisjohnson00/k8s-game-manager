import os
from flask import (
    Blueprint, render_template, current_app as app, request
)

bp = Blueprint('app', __name__, url_prefix='/')


@bp.route('/', methods=('GET', 'POST'))
def index():
    return render_template('app/list.html')
