import uuid, yaml, json, logging, pathlib
from ignition.service.framework import Service, Capability
from ignition.service.infrastructure import InfrastructureDriverCapability
from ignition.model.infrastructure import CreateInfrastructureResponse, DeleteInfrastructureResponse, FindInfrastructureResponse, InfrastructureTask, STATUS_IN_PROGRESS, STATUS_COMPLETE, STATUS_FAILED, STATUS_UNKNOWN
from ignition.model.failure import FAILURE_CODE_RESOURCE_ALREADY_EXISTS, FAILURE_CODE_UNKNOWN, FAILURE_CODE_INTERNAL_ERROR
from kubernetes.client.rest import ApiException

logger = logging.getLogger(__name__)

class K8sInfrastructureService(Service, InfrastructureDriverCapability):

    def __init__(self, tosca_translator, **kwargs):
        self.tosca_translator = tosca_translator
        if 'location_translator' not in kwargs:
            raise ValueError('location_translator argument not provided')
        self.location_translator = kwargs.get('location_translator')

    def create_infrastructure(self, template, template_type, inputs, deployment_location):
        """
        Initiates a request to create infrastructure based on a VNFC package

        :param str template: tosca template of infrastructure to be created
        :param str inputs: values for the inputs defined on the tosca template
        :param dict deployment_location: the valid Openstack location to deploy to
        :return: the id of Infrastructure to be created
        """
        infrastructure_id = uuid.uuid4().hex

        k8s = self.tosca_translator.generate_k8s(infrastructure_id, template, inputs)

        logger.debug('k8s = {0}'.format(k8s))

        k8s_location = self.location_translator.from_deployment_location(deployment_location)

        return k8s_location.create_infrastructure(infrastructure_id, k8s)

    def get_infrastructure_task(self, infrastructure_id, request_id, deployment_location):
        """
        Get information about the infrastructure (created or deleted)

        :param str infrastructure_id: identifier of the infrastructure to check
        :param str request_id: identifier of the request to check
        :param dict deployment_location: the K8s location the infrastructure was deployed to
        :return: a Infrastructure instance describing the status
        """
        # noop - the driver does not use the Ignition job queue, but sends the response directly on the infrastructure responses Kafka topic
        return None

    def delete_infrastructure(self, infrastructure_id, deployment_location):
        """
        Remove infrastructure previously created

        :param str infrastructure_id: identifier of the stack to be removed
        :param dict deployment_location: the K8s location the infrastructure was deployed to
        """
        k8s_location = self.location_translator.from_deployment_location(deployment_location)
        if k8s_location is None:
            raise ValueError("Invalid deployment location")

        k8s_location.delete_infrastructure(infrastructure_id)

        return DeleteInfrastructureResponse(infrastructure_id, infrastructure_id)

    def find_infrastructure(self, template, instance_name, deployment_location):
        # TODO
        return FindInfrastructureResponse("1", {})