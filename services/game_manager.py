from kubernetes import client
from kubernetes.client.models import V1ObjectMeta, V1StatefulSetSpec, V1DeploymentSpec, V1Pod, V1StatefulSet, \
    V1Deployment  # noqa
import services.k8s
import utilities.plugins
from utilities.config import ConfigFileReader


def get_game_details(namespace, name):
    pod_name = None
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

    env_vars = services.k8s.get_env_vars(namespace=namespace, name=name)
    game_config = ConfigFileReader(f'{game_name}.yaml'.lower()).get_config()
    plugins_enabled = utilities.plugins.supports_plugins(namespace=namespace, name=name, game_config=game_config)

    return {'name': metadata.name, 'namespace': namespace, 'replicas': replicas,
            'pod_name': pod_name, 'game_name': game_name, 'env_vars': env_vars, 'plugins_enabled': plugins_enabled}
