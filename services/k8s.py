from kubernetes import client
from kubernetes.client.models import V1StatefulSetList, V1ObjectMeta, V1StatefulSetSpec, V1DeploymentList, \
    V1DeploymentSpec
from kubernetes.client.rest import ApiException
import datetime


def get_deployments(games, namespaces):
    apps_client = client.AppsV1Api()
    for namespace in namespaces:
        deployments = apps_client.list_namespaced_deployment(namespace=namespace)  # type: V1DeploymentList
        for deployment in deployments.items:
            metadata = deployment.metadata  # type: V1ObjectMeta
            spec = deployment.spec  # type: V1DeploymentSpec
            replicas = spec.replicas
            games.append({'name': metadata.name, 'type': 'deployment', 'namespace': namespace, 'replicas': replicas})
    return games


def get_statefulsets(games, namespaces):
    apps_client = client.AppsV1Api()
    for namespace in namespaces:
        stateful_sets = apps_client.list_namespaced_stateful_set(namespace=namespace)  # type: V1StatefulSetList
        for sts in stateful_sets.items:
            metadata = sts.metadata  # type: V1ObjectMeta
            spec = sts.spec  # type: V1StatefulSetSpec
            replicas = spec.replicas
            games.append({'name': metadata.name, 'type': 'sts', 'namespace': namespace, 'replicas': replicas})
    return games


def restart_deployment(name, namespace):
    v1_apps = client.AppsV1Api()
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
