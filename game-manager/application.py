import services.k8s
import utilities.relative_time
import os
from flask import (
    Blueprint, render_template, redirect, url_for, flash
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
    return redirect(url_for('app.index'))


@bp.route('/health')
def health():
    return render_template('app/health.html')


@bp.route('/power/<cycle_type>/<deployment_type>/<namespace>/<name>')
def power_cycle(cycle_type, deployment_type, namespace, name):
    flash(f"Powering {cycle_type} {name}")
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


@bp.route('/plugins/<namespace>/<name>/<game_name>')
def list_plugins(namespace, name, game_name):
    base_path = "/game-mounts"
    pvc_volume = services.k8s.get_pvc_volume(namespace=namespace, name=name)
    plugin_path = {'rust': 'oxide/plugins'}
    pvc_path = f'{base_path}/{namespace}-{name}-{pvc_volume}/'
    full_path = f'{pvc_path}{plugin_path[game_name]}/'
    print(full_path)
    files = []
    if os.path.exists(full_path):
        files = os.listdir(full_path)
    else:
        print(f"Didn't find {full_path}")
    print(files)
    return render_template('app/plugin_list.html', files=files)
