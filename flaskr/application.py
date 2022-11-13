from flask import (
    Blueprint, render_template
)
from kubernetes import client
from kubernetes.client.models import V1StatefulSetList, V1ObjectMeta

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


@bp.route('/health')
def health():
    return render_template('app/health.html')
