
import logging
import ignition.boot.api as ignition
import k8svimdriver.config as k8svimdriverconfig
import pathlib
import os
from k8svimdriver.service.infrastructure import K8sInfrastructureService
from k8svimdriver.k8s.environment import K8sDeploymentLocationTranslator
from k8svimdriver.toscak8s.translator import ToscaK8sTranslator

default_config_dir_path = str(pathlib.Path(k8svimdriverconfig.__file__).parent.resolve())
default_config_path = os.path.join(default_config_dir_path, 'k8s_config.yml')

def create_app():
    logging.basicConfig(level=logging.INFO)

    app_builder = ignition.build_vim_driver('K8s VIM Driver')
    app_builder.include_file_config_properties(default_config_path, required=True)
    app_builder.include_file_config_properties('./k8s_config.yml', required=False)
    # custom config file e.g. for K8s populated from Helm chart values
    app_builder.include_file_config_properties('/var/k8svd/k8s_config.yml', required=False)
    app_builder.include_environment_config_properties('K8S_CONFIG', required=False)
    app_builder.add_service(K8sInfrastructureService, K8sDeploymentLocationTranslator(), ToscaK8sTranslator())

    return app_builder.configure()

def init_app():
    app = create_app()
    return app.run()
