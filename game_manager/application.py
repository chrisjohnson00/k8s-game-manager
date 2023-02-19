import services.k8s
import services.game_manager
import utilities.relative_time
import utilities.plugins
import utilities.request
from utilities.config import ConfigFileReader
import utilities.file_name_security
import os
from flask import (
    Blueprint, render_template, redirect, url_for, flash, request, current_app as app, jsonify
)
from werkzeug.utils import secure_filename

bp = Blueprint('app', __name__, url_prefix='/')


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
    game = services.game_manager.get_game_details(namespace=namespace, name=name, deployment_type=deployment_type)
    game_config = ConfigFileReader(f'{game["game_name"].title()}.yaml'.lower()).get_config()
    pod = None
    pod_running_since = None
    if game['pod_name']:
        pod = services.k8s.get_pod_details(namespace=namespace, pod_name=game['pod_name'])
        if pod.status.start_time:
            pod_running_since = utilities.relative_time.relative_time(pod.status.start_time)

    return render_template('app/details.html', game=game, pod=pod, pod_running_since=pod_running_since,
                           game_config=game_config)


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
    files.sort()
    return render_template('app/plugin_list.html', files=files, namespace=namespace, name=name, game_name=game_name,
                           deployment_type=deployment_type)


@bp.route('/plugin/configs/<deployment_type>/<namespace>/<name>/<game_name>')
def list_plugin_configs(deployment_type, namespace, name, game_name):
    game_config = ConfigFileReader(f'{game_name}.yaml'.lower()).get_config()
    full_path = utilities.plugins.get_path_to_plugin_configs(name=name, namespace=namespace, game_config=game_config)
    files = []
    if os.path.exists(full_path):
        files = os.listdir(full_path)
    else:
        app.logger.info(f"Didn't find {full_path}")
    files.sort()
    return render_template('app/plugin_config_list.html', files=files, namespace=namespace, name=name,
                           game_name=game_name, deployment_type=deployment_type)


@bp.route('/plugin/delete/<deployment_type>/<namespace>/<name>/<game_name>')
def delete_plugin(deployment_type, namespace, name, game_name):
    args = request.args
    file_name = args.get("file_name")
    utilities.file_name_security.safe_file_name(file_name)
    full_path = utilities.plugins.get_path_to_plugins(game_name, name, namespace)
    flash(f"Deleted {file_name}")
    delete_path = f'{full_path}/{file_name}'
    app.logger.info(f"Deleting {delete_path}")
    os.remove(delete_path)
    return redirect(
        url_for('app.details', namespace=namespace, name=name, game_name=game_name, deployment_type=deployment_type))


@bp.route('/plugin/upload/<deployment_type>/<namespace>/<name>/<game_name>', methods=['POST'])
def upload_plugin(deployment_type, namespace, name, game_name):
    # check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('app.details', namespace=namespace, name=name, game_name=game_name,
                                deployment_type=deployment_type))
    file = request.files['file']
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('app.details', namespace=namespace, name=name, game_name=game_name,
                                deployment_type=deployment_type))
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(utilities.plugins.get_path_to_plugins(game_name, name, namespace), filename))
        flash(f'{file.filename} has been uploaded')
        app.logger.info(f'{file.filename} has been uploaded')
        return redirect(url_for('app.details', namespace=namespace, name=name, game_name=game_name,
                                deployment_type=deployment_type))


@bp.route('/plugin/config/edit/<deployment_type>/<namespace>/<name>/<game_name>')
def edit_plugin_config_file(deployment_type, namespace, name, game_name):
    config_file_path, file_name = plugin_config_request_processing(game_name, name, namespace)
    file = open(config_file_path, mode='r')
    content = file.read()
    app.logger.info(f"Editing {config_file_path}")
    return render_template('app/plugin_config_edit.html', file=file_name, file_content=content, namespace=namespace,
                           name=name, game_name=game_name, deployment_type=deployment_type)


def plugin_config_request_processing(game_name, name, namespace):
    args = request.args
    file_name = args.get("file_name")
    utilities.file_name_security.safe_file_name(file_name)
    game_config = ConfigFileReader(f'{game_name}.yaml'.lower()).get_config()
    if game_config['plugins']['configs']['type'] != 'json':
        raise ValueError("Only plugin config files of type JSON are supported")
    full_path = utilities.plugins.get_path_to_plugin_configs(name=name, namespace=namespace, game_config=game_config)
    config_file_path = f'{full_path}{file_name}'
    return config_file_path, file_name


@bp.route('/plugin/config/update/<namespace>/<name>/<game_name>', methods=['PUT'])
def update_plugin_config_file(namespace, name, game_name):
    config_file_path, file_name = plugin_config_request_processing(game_name, name, namespace)
    app.logger.info(f"Updating {config_file_path}")
    app.logger.debug(request.json['json'])
    file = open(config_file_path, mode='w')
    file.write(request.json['json'])
    return jsonify(success=True)


@bp.route('/config', methods=['POST'])
def update_environment_variable():
    namespace = request.form.get('namespace')
    name = request.form.get('name')
    extra_parameters = utilities.request.get_unknown_params(['namespace', 'name'], request)
    keys = [d['key'] for d in extra_parameters]
    values = [d['value'] for d in extra_parameters]
    app.logger.debug(f'Updating env var -- Namespace: {namespace}, Name: {name}, Env Var {keys[0]}={values[0]}')
    services.k8s.update_statefulset_env(namespace, name, env_key=keys[0], env_value=values[0])
    return jsonify(success=True)
