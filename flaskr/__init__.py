from logging.config import dictConfig
from flask import Flask
import os
from kubernetes import config


def create_app():
    dictConfig({
        'version': 1,
        'formatters': {'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }},
        'handlers': {'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
            'formatter': 'default'
        }},
        'root': {
            'level': 'INFO',
            'handlers': ['wsgi']
        }
    })
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    from . import application

    if os.environ.get('USE_K8S_CONFIG_FILE'):
        config.load_kube_config()
    else:
        config.load_incluster_config()

    app.register_blueprint(application.bp)

    return app
