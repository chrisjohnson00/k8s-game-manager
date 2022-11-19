import services.k8s
import utilities.relative_time
import utilities.plugins
import os
from flask import (
    Blueprint, render_template, redirect, url_for, flash, request, current_app as app
)

bp = Blueprint('app', __name__, url_prefix='/')
GAMES_WHICH_SUPPORT_PLUGINS = ['rust']


@bp.route('/')
def index():
    sts_namespaces = ['rust']
    deploy_namespaces = ['minecraft']
    games = []
    games = services.k8s.get_statefulsets(games, sts_namespaces)
    games = services.k8s.get_deployments(games, deploy_namespaces)
    return render_template('app/list.html', games=games)


@bp.route('/restart/<deployment_type>/<namespace>/<name>')
def restart(deployment_type, namespace, name):
    services.k8s.restart_game_deployment(namespace, deployment_type, name)
    flash(f"Restarted {name}")
    app.logger.info(f"Restarted {name}")
    return redirect(url_for('app.index'))


@bp.route('/health')
def health():
    return render_template('app/health.html')


@bp.route('/power/<cycle_type>/<deployment_type>/<namespace>/<name>')
def power_cycle(cycle_type, deployment_type, namespace, name):
    flash(f"Powering {cycle_type} {name}")
    app.logger.info(f"Powering {cycle_type} {name}")
    if cycle_type == "on":
        services.k8s.scale(namespace, deployment_type, name, 1)
    elif cycle_type == "off":
        services.k8s.scale(namespace, deployment_type, name, 0)
    else:
        raise ValueError(f'{cycle_type} is not a valid cycle type')
    return redirect(url_for('app.index'))


@bp.route('/details/<deployment_type>/<namespace>/<name>')
def details(deployment_type, namespace, name):
    game = services.k8s.get_game_details(namespace=namespace, name=name, deployment_type=deployment_type)
    pod = None
    pod_running_since = None
    if game['pod_name']:
        pod = services.k8s.get_pod_details(namespace=namespace, pod_name=game['pod_name'])
        if pod.status.start_time:
            pod_running_since = utilities.relative_time.relative_time(pod.status.start_time)

    return render_template('app/details.html', game=game, pod=pod, pod_running_since=pod_running_since,
                           games_which_support_plugins=GAMES_WHICH_SUPPORT_PLUGINS)


@bp.route('/logs/<namespace>/<name>')
def logs(namespace, name):
    pod_logs = services.k8s.get_logs(namespace=namespace, pod_name=name)
    return render_template('app/logs.html', logs=pod_logs)


@bp.route('/plugins/<deployment_type>/<namespace>/<name>/<game_name>')
def list_plugins(deployment_type, namespace, name, game_name):
    full_path = utilities.plugins.get_path_to_plugins(game_name, name, namespace)
    files = []
    if os.path.exists(full_path):
        files = os.listdir(full_path)
    else:
        app.logger.info(f"Didn't find {full_path}")
    return render_template('app/plugin_list.html', files=files, namespace=namespace, name=name, game_name=game_name,
                           deployment_type=deployment_type)


@bp.route('/plugin/delete/<deployment_type>/<namespace>/<name>/<game_name>')
def delete_plugin(deployment_type, namespace, name, game_name):
    args = request.args
    file_name = args.get("file_name")
    full_path = utilities.plugins.get_path_to_plugins(game_name, name, namespace)
    flash(f"Deleted {file_name}")
    delete_path = f'{full_path}/{file_name}'
    app.logger.info(f"Deleting {delete_path}")
    os.remove(delete_path)
    return redirect(
        url_for('app.details', namespace=namespace, name=name, game_name=game_name, deployment_type=deployment_type))
