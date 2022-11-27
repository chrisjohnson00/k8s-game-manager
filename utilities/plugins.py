import services.k8s
from kubernetes.client.models import V1EnvVar


def get_path_to_plugins(game_name, name, namespace):
    base_path = "/game-mounts"
    pvc_volume = services.k8s.get_pvc_volume(namespace=namespace, name=name)
    plugin_path = {'rust': 'oxide/plugins'}
    pvc_path = f'{base_path}/{namespace}-{name}-{pvc_volume}/'
    full_path = f'{pvc_path}{plugin_path[game_name]}/'
    return full_path


def supports_plugins(namespace, name, game_name, deployment_type):
    env_vars = services.k8s.get_env_vars(namespace=namespace, name=name,
                                         deployment_type=deployment_type)  # type: list[V1EnvVar]
    env_var_that_says_plugins_are_enabled = {'rust': 'RUST_OXIDE_ENABLED', 'minecraft': 'foobar'}
    for v in env_vars:
        if env_var_that_says_plugins_are_enabled[game_name] == v.name:
            return True
    return False
