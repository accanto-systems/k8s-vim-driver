
import logging
import ignition.boot.api as ignition
from ignition.service.infrastructure import InfrastructureMessagingCapability
import k8svimdriver.config as k8svimdriverconfig
import pathlib
import os
from k8svimdriver.service.infrastructure import K8sInfrastructureService
from k8svimdriver.k8s.environment import K8sDeploymentLocationTranslator
from k8svimdriver.toscak8s.translator import ToscaK8sTranslator
from k8svimdriver.service.k8s import K8sProperties

default_config_dir_path = str(pathlib.Path(k8svimdriverconfig.__file__).parent.resolve())
default_config_path = os.path.join(default_config_dir_path, 'k8s_config.yml')

def create_app():
    app_builder = ignition.build_vim_driver('K8s VIM Driver')
    app_builder.include_file_config_properties(default_config_path, required=True)
    app_builder.include_file_config_properties('./k8s_config.yml', required=False)
    # custom config file e.g. for K8s populated from Helm chart values
    app_builder.include_file_config_properties('/var/k8svd/k8s_config.yml', required=False)
    app_builder.include_environment_config_properties('K8S_CONFIG', required=False)
    k8s_properties = K8sProperties()
    app_builder.add_property_group(k8s_properties)

    app_builder.add_service(K8sDeploymentLocationTranslator, k8s_properties, inf_messaging_service=InfrastructureMessagingCapability)
    app_builder.add_service(K8sInfrastructureService, ToscaK8sTranslator(), location_translator=K8sDeploymentLocationTranslator)

    return app_builder.configure()

def init_app():
    app = create_app()
    return app.run()
