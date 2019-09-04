import yaml, logging
from toscaparser.functions import GetInput
from toscaparser.tosca_template import ToscaTemplate

logger = logging.getLogger(__name__)

class ToscaK8sTranslator():

    def __parse_tosca_str(self, tosca_template, inputs):
        tosca = yaml.safe_load(tosca_template)
        return ToscaTemplate(None, inputs, False, tosca)

    def get_prop_value(self, props, name):
        if(isinstance(props[name].value, GetInput)):
            return props[name].value.result()
        else:
            return props[name].value

    def generate_k8s(self, tosca_template, inputs):
        if tosca_template is None:
            raise ValueError('Must provide a tosca_template parameter')
        tosca = self.__parse_tosca_str(tosca_template, inputs)

        k8s = {
            'pods': [],
            'storage': {}
        }

        # node_templates = [nt for nt in tosca.topology_template.nodetemplates]

        # get storage config first
        for node_template in tosca.topology_template.nodetemplates:
        # for node_template in node_templates:
            node_type = node_template.type_definition.ntype

            if(node_type == 'accanto.nodes.K8sStorage'):
                props = node_template.get_properties()
                k8s['storage'][node_template.name] = {
                    'name': node_template.name,
                    'size': self.get_prop_value(props, 'size'),
                    'storageClassName': self.get_prop_value(props, 'class')
                }

        # get compute config
        for node_template in tosca.topology_template.nodetemplates:
        # for node_template in node_templates:
            node_type = node_template.type_definition.ntype
            podStorage = []
            for element in node_template.requirements:
                if len(element.values()) > 0:
                    req = list(element.values())[0]
                    if isinstance(req, dict):
                        capability = req.get("capability", None)
                        if capability is None:
                            raise ValueError('Missing capability on requirement {}'.format(str(req)))
                        storageName = req.get("node", None)
                        if storageName is None:
                            raise ValueError('Missing node on requirement {}'.format(str(req)))
                        if capability == "tosca.capabilities.Attachment":
                            rel = req.get("relationship", None)
                            if rel is not None:
                                props = rel.get("properties", {})
                                mount_location = props.get("location", None)
                                if mount_location is None:
                                    raise ValueError('Must provide a mount location')

                                storageDef = k8s['storage'].get(storageName, None)
                                if storageDef is None:
                                    raise ValueError('Compute references not-existent storage')

                                podStorage.append({
                                    "name": storageName,
                                    "size": storageDef['size'],
                                    "storageClassName": storageDef['storageClassName'],
                                    "mountPath": mount_location
                                })

            if(node_type == 'accanto.nodes.K8sCompute'):
                props = node_template.get_properties()
                k8s['pods'].append({
                    'name': node_template.name,
                    'image': self.get_prop_value(props, 'image'),
                    'container_port': self.get_prop_value(props, 'container_port'),
                    'storage': podStorage
                })
        
        return k8s
