from flask import (
    Blueprint, render_template, redirect, url_for, flash
)
from kubernetes import client
from kubernetes.client.models import V1StatefulSetList, V1ObjectMeta, V1StatefulSetSpec, V1DeploymentList, \
    V1DeploymentSpec
from kubernetes.client.rest import ApiException
import datetime

bp = Blueprint('app', __name__, url_prefix='/')


@bp.route('/')
def index():
    sts_namespaces = ['rust']
    deploy_namespaces = ['minecraft']
    apps_client = client.AppsV1Api()
    games = []
    games = get_statefulsets(apps_client, games, sts_namespaces)
    games = get_deployments(apps_client, games, deploy_namespaces)
    return render_template('app/list.html', games=games)


def get_deployments(apps_client, games, namespaces):
    for namespace in namespaces:
        deployments = apps_client.list_namespaced_deployment(namespace=namespace)  # type: V1DeploymentList
        for deployment in deployments.items:
            metadata = deployment.metadata  # type: V1ObjectMeta
            spec = deployment.spec  # type: V1DeploymentSpec
            replicas = spec.replicas
            games.append({'name': metadata.name, 'type': 'deployment', 'namespace': namespace, 'replicas': replicas})
    return games


def get_statefulsets(apps_client, games, namespaces):
    for namespace in namespaces:
        stateful_sets = apps_client.list_namespaced_stateful_set(namespace=namespace)  # type: V1StatefulSetList
        for sts in stateful_sets.items:
            metadata = sts.metadata  # type: V1ObjectMeta
            spec = sts.spec  # type: V1StatefulSetSpec
            replicas = spec.replicas
            games.append({'name': metadata.name, 'type': 'sts', 'namespace': namespace, 'replicas': replicas})
    return games


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
