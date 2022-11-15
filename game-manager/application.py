from flask import (
    Blueprint, render_template, redirect, url_for, flash
)
from services.k8s import get_deployments, get_statefulsets, restart_deployment

bp = Blueprint('app', __name__, url_prefix='/')


@bp.route('/')
def index():
    sts_namespaces = ['rust']
    deploy_namespaces = ['minecraft']
    games = []
    games = get_statefulsets(games, sts_namespaces)
    games = get_deployments(games, deploy_namespaces)
    return render_template('app/list.html', games=games)


@bp.route('/restart')
def restart():
    restart_deployment("rust-lg", "rust")
    flash("Restarted rust-lg")
    return redirect(url_for('app.index'))


@bp.route('/health')
def health():
    return render_template('app/health.html')
