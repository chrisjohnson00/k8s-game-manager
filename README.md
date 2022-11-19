# game-manager
A Game Manger on top of kubernetes deployments for various video games.

PyPi Dependency updates

    pip install --upgrade pip
    pip install --upgrade Flask gunicorn kubernetes
    pip freeze > requirements.txt
    sed -i '/pkg_resources/d' requirements.txt

## Running locally

```commandline
export FLASK_APP=game_manager
export USE_K8S_CONFIG_FILE=true
export KUBECONFIG=~/.kube/game_config
flask --debug run
```