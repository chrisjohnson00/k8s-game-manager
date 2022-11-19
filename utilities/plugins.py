import services.k8s


def get_path_to_plugins(game_name, name, namespace):
    base_path = "/game-mounts"
    pvc_volume = services.k8s.get_pvc_volume(namespace=namespace, name=name)
    plugin_path = {'rust': 'oxide/plugins'}
    pvc_path = f'{base_path}/{namespace}-{name}-{pvc_volume}/'
    full_path = f'{pvc_path}{plugin_path[game_name]}/'
    return full_path
