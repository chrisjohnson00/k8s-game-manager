from kubernetes import client
from kubernetes.client.models import V1StatefulSetList, V1ObjectMeta, V1StatefulSetSpec, V1DeploymentList, \
    V1DeploymentSpec, V1Pod
from kubernetes.client.rest import ApiException
from kubernetes.client.api.core_v1_api import CoreV1Api
import datetime


def get_deployments(games, namespaces):
    apps_client = client.AppsV1Api()
    for namespace in namespaces:
        deployments = apps_client.list_namespaced_deployment(namespace=namespace)  # type: V1DeploymentList
        for deployment in deployments.items:
            metadata = deployment.metadata  # type: V1ObjectMeta
            spec = deployment.spec  # type: V1DeploymentSpec
            replicas = spec.replicas
            games.append(
                {'name': metadata.name, 'deployment_type': 'deployment', 'namespace': namespace, 'replicas': replicas})
    return games


def get_statefulsets(games, namespaces):
    apps_client = client.AppsV1Api()
    for namespace in namespaces:
        stateful_sets = apps_client.list_namespaced_stateful_set(namespace=namespace)  # type: V1StatefulSetList
        for sts in stateful_sets.items:
            metadata = sts.metadata  # type: V1ObjectMeta
            spec = sts.spec  # type: V1StatefulSetSpec
            replicas = spec.replicas
            games.append(
                {'name': metadata.name, 'deployment_type': 'statefulset', 'namespace': namespace, 'replicas': replicas})
    return games


def restart_game_deployment(namespace, deployment_type, name):
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
    if deployment_type == 'statefulset':
        try:
            v1_apps.patch_namespaced_stateful_set(name, namespace, body, pretty='true')
        except ApiException as e:
            print("Exception when calling AppsV1Api->patch_namespaced_stateful_set: %s\n" % e)
            raise e
    elif deployment_type == 'deployment':
        try:
            v1_apps.patch_namespaced_deployment(name, namespace, body, pretty='true')
        except ApiException as e:
            print("Exception when calling AppsV1Api->patch_namespaced_deployment: %s\n" % e)
            raise e
    else:
        raise ValueError(f'{deployment_type} is not a valid deployment type')


def scale(namespace, deployment_type, name, new_replica_count):
    v1_apps = client.AppsV1Api()
    body = {
        'spec': {
            'replicas': new_replica_count
        }
    }
    if deployment_type == 'statefulset':
        try:
            v1_apps.patch_namespaced_stateful_set(name, namespace, body, pretty='true')
        except ApiException as e:
            print("Exception when calling AppsV1Api->patch_namespaced_stateful_set: %s\n" % e)
            raise e
    elif deployment_type == 'deployment':
        try:
            v1_apps.patch_namespaced_deployment(name, namespace, body, pretty='true')
        except ApiException as e:
            print("Exception when calling AppsV1Api->patch_namespaced_deployment: %s\n" % e)
            raise e
    else:
        raise ValueError(f'{deployment_type} is not a valid deployment type')


def get_game_details(namespace, name, deployment_type):
    pod_name = None
    if deployment_type == "statefulset":
        apps_client = client.AppsV1Api()
        sts = apps_client.read_namespaced_stateful_set(namespace=namespace, name=name)
        metadata = sts.metadata  # type: V1ObjectMeta
        spec = sts.spec  # type: V1StatefulSetSpec
        replicas = spec.replicas
        if replicas > 0:
            pod_name = f'{metadata.name}-0'
        return {'name': metadata.name, 'deployment_type': deployment_type, 'namespace': namespace, 'replicas': replicas,
                'pod_name': pod_name}
    elif deployment_type == "deployment":
        apps_client = client.AppsV1Api()
        deployment = apps_client.read_namespaced_deployment(namespace=namespace, name=name)
        metadata = deployment.metadata  # type: V1ObjectMeta
        spec = deployment.spec  # type: V1DeploymentSpec
        replicas = spec.replicas
        if replicas > 0:
            pods = get_pods_matching_label(namespace=namespace, label=f"app={name}")
            # It seems that right after a restart there could be a time where this returns no pods
            if len(pods.items) > 0:
                pod = pods.items.pop()  # type: V1Pod
                pod_name = pod.metadata.name
        return {'name': metadata.name, 'deployment_type': deployment_type, 'namespace': namespace, 'replicas': replicas,
                'pod_name': pod_name}
    else:
        raise ValueError(f'{deployment_type} is not a valid deployment type')


def get_logs(namespace, pod_name):
    try:
        core_client = client.CoreV1Api()  # type: CoreV1Api
        logs = core_client.read_namespaced_pod_log(name=pod_name, namespace=namespace, tail_lines=25)
        return logs
    except ApiException as e:
        print("Exception when calling CoreV1Api->read_namespaced_pod_log: %s\n" % e)
        return ""


def get_pod_details(namespace, pod_name):
    core_client = client.CoreV1Api()  # type: CoreV1Api
    pod = core_client.read_namespaced_pod(name=pod_name, namespace=namespace)  # type: V1Pod
    return pod


def get_pods_matching_label(namespace, label):
    core_client = client.CoreV1Api()  # type: CoreV1Api
    pod_list = core_client.list_namespaced_pod(namespace=namespace, label_selector=label)
    return pod_list
