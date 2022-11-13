from flask import (
    Blueprint, render_template
)

bp = Blueprint('app', __name__, url_prefix='/')


@bp.route('/', methods=('GET'))
def index():
    return render_template('app/list.html')


@bp.route('/health', methods='GET')
def health():
    return render_template('app/list.html')
