import services.k8s
from kubernetes.client.models import V1EnvVar  # noqa

pvc_base_path = "/game-mounts"


def get_path_to_plugins(game_name, name, namespace):
    pvc_volume = services.k8s.get_pvc_volume(namespace=namespace, name=name)
    # TODO replace with values from config
    plugin_path = {'rust': 'oxide/plugins'}
    pvc_path = f'{pvc_base_path}/{namespace}-{name}-{pvc_volume}/'
    full_path = f'{pvc_path}{plugin_path[game_name]}/'
    return full_path


def get_path_to_plugin_configs(name, namespace, game_config):
    pvc_volume = services.k8s.get_pvc_volume(namespace=namespace, name=name)
    config_path = game_config['plugins']['configs']['path']
    pvc_path = f'{pvc_base_path}/{namespace}-{name}-{pvc_volume}/'
    full_path = f'{pvc_path}{config_path}/'
    return full_path


def supports_plugins(namespace, name, game_config):
    env_vars = services.k8s.get_env_vars(namespace=namespace, name=name)  # type: list[V1EnvVar]
    enabled_by_name = game_config['plugins']['enabledBy']['name']
    enabled_by_value = game_config['plugins']['enabledBy']['value']
    for v in env_vars:
        if enabled_by_name == v.name and enabled_by_value == v.value:
            return True
    return False
