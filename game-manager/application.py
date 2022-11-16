from flask import (
    Blueprint, render_template, redirect, url_for, flash
)
from services.k8s import get_deployments, get_statefulsets, restart_game_deployment, scale, get_game_details, get_logs

bp = Blueprint('app', __name__, url_prefix='/')


@bp.route('/')
def index():
    sts_namespaces = ['rust']
    deploy_namespaces = ['minecraft']
    games = []
    games = get_statefulsets(games, sts_namespaces)
    games = get_deployments(games, deploy_namespaces)
    return render_template('app/list.html', games=games)


@bp.route('/restart/<deployment_type>/<namespace>/<name>')
def restart(deployment_type, namespace, name):
    restart_game_deployment(namespace, deployment_type, name)
    flash(f"Restarted {name}")
    return redirect(url_for('app.index'))


@bp.route('/health')
def health():
    return render_template('app/health.html')


@bp.route('/power/<cycle_type>/<deployment_type>/<namespace>/<name>')
def power_cycle(cycle_type, deployment_type, namespace, name):
    flash(f"Powering {cycle_type} {name}")
    if cycle_type == "on":
        scale(namespace, deployment_type, name, 1)
    elif cycle_type == "off":
        scale(namespace, deployment_type, name, 0)
    else:
        raise ValueError(f'{cycle_type} is not a valid cycle type')
    return redirect(url_for('app.index'))


@bp.route('/details/<deployment_type>/<namespace>/<name>')
def details(deployment_type, namespace, name):
    game = get_game_details(namespace=namespace, name=name, deployment_type=deployment_type)
    return render_template('app/details.html', game=game)


@bp.route('/logs/<namespace>/<name>')
def logs(namespace, name):
    pod_logs = get_logs(namespace=namespace, pod_name=name)
    return render_template('app/logs.html', logs=pod_logs)
