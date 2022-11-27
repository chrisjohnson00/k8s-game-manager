from kubernetes import client
from kubernetes.client.models import V1ObjectMeta, V1StatefulSetSpec, V1DeploymentSpec, V1Pod, V1StatefulSet, \
    V1Deployment
import services.k8s
import utilities.plugins


def get_game_details(namespace, name, deployment_type):
    pod_name = None
    if deployment_type == "statefulset":
        apps_client = client.AppsV1Api()
        sts = apps_client.read_namespaced_stateful_set(namespace=namespace, name=name)  # type: V1StatefulSet
        metadata = sts.metadata  # type: V1ObjectMeta
        spec = sts.spec  # type: V1StatefulSetSpec
        replicas = spec.replicas
        if replicas > 0:
            pod_name = f'{metadata.name}-0'
        game_name = services.k8s.get_annotation_by_name("game", sts)
    elif deployment_type == "deployment":
        apps_client = client.AppsV1Api()
        deployment = apps_client.read_namespaced_deployment(namespace=namespace, name=name)  # type: V1Deployment
        metadata = deployment.metadata  # type: V1ObjectMeta
        spec = deployment.spec  # type: V1DeploymentSpec
        replicas = spec.replicas
        if replicas > 0:
            pods = services.k8s.get_pods_matching_label(namespace=namespace, label=f"app={name}")
            # It seems that right after a restart there could be a time where this returns no pods
            if len(pods.items) > 0:
                pod = pods.items.pop()  # type: V1Pod
                pod_name = pod.metadata.name
        game_name = services.k8s.get_annotation_by_name("game", deployment)
    else:
        raise ValueError(f'{deployment_type} is not a valid deployment type')

    env_vars = services.k8s.get_env_vars(namespace=namespace, name=name, deployment_type=deployment_type)
    plugins_enabled = utilities.plugins.supports_plugins(namespace=namespace, name=name,
                                                         deployment_type=deployment_type, game_name=game_name)

    return {'name': metadata.name, 'deployment_type': deployment_type, 'namespace': namespace, 'replicas': replicas,
            'pod_name': pod_name, 'game_name': game_name, 'env_vars': env_vars, 'plugins_enabled': plugins_enabled}
