import yaml, logging
from toscaparser.functions import GetInput
from toscaparser.tosca_template import ToscaTemplate
from toscaparser.functions import GetAttribute

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

    def find_node_template_with_name(self, node_templates, name):
        logger.info('Finding node template with name {0}'.format(name))

        matching_node_templates = list(filter(lambda node_template: node_template.name == name, node_templates))
        logger.info('Matching node templates {0}'.format(str(matching_node_templates)))
        if len(matching_node_templates) > 0:
            logger.info('Matching node template {0}'.format(str(matching_node_templates[0])))
            return matching_node_templates[0]
        else:
            return None

    def process_output(self, tosca, k8s, output):
        logger.info('Processing output {0}'.format(output))

        node_templates = tosca.topology_template.nodetemplates
        output_name = output.name
        value = output.attrs['value']
        if isinstance(value, GetAttribute):
            attr_name = value.attribute_name
            logger.info("Got attribute with name {0}".format(attr_name))

            matching_node_template = self.find_node_template_with_name(node_templates, value.node_template_name)
            if matching_node_template is not None and matching_node_template.type == 'accanto.nodes.K8sNetwork' and attr_name == 'address':
                # net_name e.g. mgmt
                net_name = matching_node_template.get_properties().get('name', None)
                logger.info('k8s1 = {0}, net_name = {1}, output_name = {2}'.format(str(k8s), net_name.value, output_name))
                if net_name is not None and net_name.value is not None:
                    k8s['outputs'][output_name] = "network." + net_name.value
                logger.info('k8s2 = {0}, net_name = {1}, output_name = {2}'.format(str(k8s), net_name.value, output_name))

    def generate_k8s(self, infrastructure_id, tosca_template, inputs):
        if tosca_template is None:
            raise ValueError('Must provide a tosca_template parameter')
        tosca = self.__parse_tosca_str(tosca_template, inputs)

        k8s = {
            'pods': [],
            'storage': {},
            'networks': {},
            'outputs': {}
        }

        resource_name = inputs.get('resourceName', infrastructure_id)

        # get storage and network config first
        for node_template in tosca.topology_template.nodetemplates:
            node_type = node_template.type_definition.ntype

            if(node_type == 'accanto.nodes.K8sStorage'):
                props = node_template.get_properties()
                k8s['storage'][node_template.name] = {
                    'name': self.normalize_name(resource_name + '_' + node_template.name),
                    'size': self.get_prop_value(props, 'size'),
                    'storageClassName': self.get_prop_value(props, 'class')
                }
            elif(node_type == 'accanto.nodes.K8sNetwork'):
                props = node_template.get_properties()
                k8s['networks'][node_template.name] = {
                    'name': self.normalize_name(resource_name + '_' + node_template.name)
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
                                        "name": self.normalize_name(resource_name + '_' + targetNodeName),
                                        "size": storageDef['size'],
                                        "storageClassName": storageDef['storageClassName'],
                                        "mountPath": mount_location
                                    })
                                elif rel_type == 'tosca.relationships.ConnectsTo':
                                    network = k8s['networks'].get(targetNodeName, None)
                                    if network is None:
                                        raise ValueError('Compute references not-existent network')

                                    network_name = network.get('name', None)
                                    if network_name is None:
                                        raise ValueError('Network node template {0} does not have a name'.format(network_name))
                                    else:
                                        podNetworks.append({
                                            "name": network_name
                                        })
                        else:
                            pass

            if(node_type == 'accanto.nodes.K8sCompute'):
                props = node_template.get_properties()
                k8s['pods'].append({
                    'name': self.normalize_name(resource_name + '_' + node_template.name),
                    'image': self.get_prop_value(props, 'image'),
                    'container_port': self.get_prop_value(props, 'container_port'),
                    'storage': podStorage,
                    'network': podNetworks
                })

            for output in tosca.topology_template.outputs:
                logger.info('Processing output {0}'.format(str(output)))
                self.process_output(tosca, k8s, output)

        logger.info('k8s = {0}'.format(k8s))

        return k8s
