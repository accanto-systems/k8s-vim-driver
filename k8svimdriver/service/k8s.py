from ignition.service.config import ConfigurationPropertiesGroup

class K8sProperties(ConfigurationPropertiesGroup):
    def __init__(self):
        super().__init__('k8s')
        self.tmpdir = "./"
