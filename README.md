# game-manager
A Game Manger on top of kubernetes deployments for various video games.

PyPi Dependency updates

    docker run -it --rm -v ${PWD}:/repo -w /repo python:3.11.2-slim bash
    pip install --upgrade pip
    pip install --upgrade Flask gunicorn kubernetes pyyaml
    pip freeze > requirements.txt
    sed -i '/pkg_resources/d' requirements.txt

## Running locally

```commandline
export FLASK_APP=game_manager
export USE_K8S_CONFIG_FILE=true
export KUBECONFIG=~/.kube/game_config
flask --debug run
```

## Deploying to K8s

If you are running microk8s as your game server, a deploy is as simple as `kubectl apply -f kubernetes`, this will apply
all the resources defined in the `kubernetes` directory.

By default, the host mount path is `/var/snap/microk8s/common/default-storage`, which is the location that all PVCs
are created by microk8s.  If you need to change this, I'd suggest using Kustomize to patch with your value, for example:

```yaml
  apiVersion: apps/v1
  kind: Deployment
  metadata:
    name: game-manager
    namespace: game-manager
  spec:
    template:
      spec:
        volumes:
          - name: game-mounts
            hostPath:
              path: /your/different/path/here
```