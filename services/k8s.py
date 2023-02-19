from kubernetes import client
from kubernetes.client.models import V1StatefulSetList, V1ObjectMeta, V1StatefulSetSpec, V1DeploymentList, \
    V1DeploymentSpec, V1Pod, V1StatefulSet, V1Deployment, V1PersistentVolumeClaim, V1PersistentVolumeClaimSpec, \
    V1PodTemplateSpec, V1PodSpec, V1Container, V1EnvVar, V1LabelSelector, V1DeploymentStrategy  # noqa
from kubernetes.client.rest import ApiException
from kubernetes.client.api.core_v1_api import CoreV1Api  # noqa
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


def get_annotation_by_name(name, thing):
    metadata = thing.metadata  # type: V1ObjectMeta
    annotations = metadata.annotations  # type: dict
    if name in annotations.keys():
        return annotations[name]
    else:
        return None


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


def get_pvc(namespace, name):
    core_client = client.CoreV1Api()  # type: CoreV1Api
    pvc = core_client.read_namespaced_persistent_volume_claim(namespace=namespace, name=name)
    return pvc


def get_pvc_volume(namespace, name):
    pvc = get_pvc(namespace=namespace, name=name)  # type: V1PersistentVolumeClaim
    metadata = pvc.spec  # type: V1PersistentVolumeClaimSpec
    return metadata.volume_name


def get_env_vars(namespace, name, deployment_type):
    if deployment_type == "statefulset":
        apps_client = client.AppsV1Api()
        sts = apps_client.read_namespaced_stateful_set(namespace=namespace, name=name)  # type: V1StatefulSet
        spec = sts.spec  # type: V1StatefulSetSpec
        template = spec.template  # type: V1PodTemplateSpec
        template_spec = template.spec  # type: V1PodSpec
        containers = template_spec.containers  # type: list[V1Container]
        # so far, all sts/deployments expect a single container per pod.
        container = containers[0]  # type: V1Container
        env_vars = container.env  # type: list[V1EnvVar]
    elif deployment_type == "deployment":
        apps_client = client.AppsV1Api()
        deployment = apps_client.read_namespaced_deployment(namespace=namespace, name=name)  # type: V1Deployment
        spec = deployment.spec  # type: V1DeploymentSpec
        template = spec.template  # type: V1PodTemplateSpec
        template_spec = template.spec  # type: V1PodSpec
        containers = template_spec.containers  # type: list[V1Container]
        # so far, all sts/deployments expect a single container per pod.
        container = containers[0]  # type: V1Container
        env_vars = container.env  # type: list[V1EnvVar]
    else:
        raise ValueError(f'{deployment_type} is not a valid deployment type')
    return env_vars


def update_statefulset_env(namespace, statefulset_name, env_key, env_value):
    # Create the Kubernetes client API
    api = client.AppsV1Api()

    # Get the current StatefulSet object
    statefulset = api.read_namespaced_stateful_set(statefulset_name, namespace)

    # Get the current container spec
    container = statefulset.spec.template.spec.containers[0]

    change_needed = False

    env_value = env_value.strip()

    # Find the environment variable by key, and update its value
    env_var = next((env for env in container.env if env.name == env_key), None)
    if env_var is not None:
        if env_var.value != env_value:
            env_var.value = env_value
            change_needed = True
    else:
        container.env.append(client.V1EnvVar(name=env_key, value=env_value))
        change_needed = True

    # Update the StatefulSet with the modified container spec
    if change_needed:
        api.patch_namespaced_stateful_set(statefulset_name, namespace, statefulset)


def get_node_port(namespace, service_name):
    api = client.CoreV1Api()
    svc = api.read_namespaced_service(service_name, namespace)

    for port in svc.spec.ports:
        if port.name == "gameport":
            return port.node_port


def create_deployment(env_vars, namespace, deployment_name, container_image):
    # create a Kubernetes API client object
    api = client.AppsV1Api()

    # create the deployment object
    deployment = V1Deployment(
        metadata=V1ObjectMeta(
            name=deployment_name
        ),
        spec=V1DeploymentSpec(
            strategy=V1DeploymentStrategy(type="Recreate"),
            replicas=1,
            selector=V1LabelSelector(
                match_labels={"app": deployment_name}
            ),
            template=V1PodTemplateSpec(
                metadata=V1ObjectMeta(
                    labels={"app": deployment_name}
                ),
                spec=V1PodSpec(
                    containers=[
                        V1Container(
                            name=deployment_name,
                            image=container_image,
                            env=[V1EnvVar(name=k, value=v) for k, v in env_vars.items()]
                        )
                    ]
                )
            )
        )
    )

    # create the deployment in the specified namespace
    return api.create_namespaced_deployment(namespace=namespace, body=deployment)


def get_env_vars_from_deployment(deployment):
    containers = deployment.spec.template.spec.containers
    env_vars = []

    for container in containers:
        for env in container.env:
            env_vars.append((env.name, env.value))

    return env_vars
