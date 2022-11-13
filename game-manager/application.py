from flask import (
    Blueprint, render_template, redirect, url_for, flash
)
from kubernetes import client
from kubernetes.client.models import V1StatefulSetList, V1ObjectMeta
from kubernetes.client.rest import ApiException
import datetime

bp = Blueprint('app', __name__, url_prefix='/')


@bp.route('/')
def index():
    namespaces = ['rust']
    apps_client = client.AppsV1Api()
    games = []
    for namespace in namespaces:
        stateful_sets = apps_client.list_namespaced_stateful_set(namespace=namespace)  # type: V1StatefulSetList
        for sts in stateful_sets.items:
            sts_metadata = sts.metadata  # type: V1ObjectMeta
            games.append({'name': sts_metadata.name, 'type': 'sts', 'namespace': namespace})
    return render_template('app/list.html', games=games)


@bp.route('/restart')
def restart():
    apps_client = client.AppsV1Api()
    restart_deployment(apps_client, "rust-lg", "rust")
    flash("Restarted rust-lg")
    return redirect(url_for('app.index'))


@bp.route('/health')
def health():
    return render_template('app/health.html')


def restart_deployment(v1_apps, name, namespace):
    now = datetime.datetime.utcnow()
    now = str(now.isoformat("T") + "Z")
    body = {
        'spec': {
            'template': {
                'metadata': {
                    'annotations': {
                        'kubectl.kubernetes.io/restartedAt': now
                    }
                }
            }
        }
    }
    try:
        v1_apps.patch_namespaced_stateful_set(name, namespace, body, pretty='true')
    except ApiException as e:
        print("Exception when calling AppsV1Api->patch_namespaced_stateful_set: %s\n" % e)
