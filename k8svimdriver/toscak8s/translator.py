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

    def normalize_name(self, name):
        return name.replace("_", "-")

    def generate_k8s(self, tosca_template, inputs):
        if tosca_template is None:
            raise ValueError('Must provide a tosca_template parameter')
        tosca = self.__parse_tosca_str(tosca_template, inputs)

        k8s = {
            'pods': [],
            'storage': {},
            'network': {}
        }

        # get storage and network config first
        for node_template in tosca.topology_template.nodetemplates:
            node_type = node_template.type_definition.ntype

            if(node_type == 'accanto.nodes.K8sStorage'):
                props = node_template.get_properties()
                k8s['storage'][node_template.name] = {
                    'name': node_template.name,
                    'size': self.get_prop_value(props, 'size'),
                    'storageClassName': self.get_prop_value(props, 'class')
                }
            elif(node_type == 'accanto.nodes.K8sNetwork'):
                props = node_template.get_properties()
                k8s['network'][node_template.name] = {
                    'name': node_template.name
                }

        # get compute config
        for node_template in tosca.topology_template.nodetemplates:
            node_type = node_template.type_definition.ntype
            podStorage = []
            podNetworks = []
            for element in node_template.requirements:
                if len(element.values()) > 0:
                    req = list(element.values())[0]
                    if isinstance(req, dict):
                        capability = req.get("capability", None)
                        if capability is None:
                            raise ValueError('Missing capability on requirement {}'.format(str(req)))
                        targetNodeName = req.get("node", None)
                        if targetNodeName is None:
                            raise ValueError('Missing node on requirement {}'.format(str(req)))

                        if capability == "tosca.capabilities.Attachment":
                            rel = req.get("relationship", None)
                            if rel is not None:
                                rel_type = rel.get('type', None)
                                if rel_type is None:
                                    raise ValueError('Must provide a relationship type')
                                elif rel_type == 'tosca.relationships.AttachesTo':
                                    props = rel.get("properties", {})
                                    mount_location = props.get("location", None)
                                    if mount_location is None:
                                        raise ValueError('Must provide a mount location')

                                    storageDef = k8s['storage'].get(targetNodeName, None)
                                    if storageDef is None:
                                        raise ValueError('Compute references not-existent storage')

                                    podStorage.append({
                                        "name": self.normalize_name(targetNodeName),
                                        "size": storageDef['size'],
                                        "storageClassName": storageDef['storageClassName'],
                                        "mountPath": mount_location
                                    })
                                elif rel_type == 'tosca.relationships.ConnectsTo':
                                    networkDef = k8s['network'].get(targetNodeName, None)
                                    if networkDef is None:
                                        raise ValueError('Compute references not-existent network')

                                    podNetworks.append({
                                        "name": self.normalize_name(targetNodeName)
                                    })
                        else:
                            pass

            if(node_type == 'accanto.nodes.K8sCompute'):
                props = node_template.get_properties()
                k8s['pods'].append({
                    'name': self.normalize_name(node_template.name),
                    'image': self.get_prop_value(props, 'image'),
                    'container_port': self.get_prop_value(props, 'container_port'),
                    'storage': podStorage,
                    'network': podNetworks
                })
        
        return k8s
