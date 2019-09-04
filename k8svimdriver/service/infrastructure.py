import uuid, yaml, json, sys, logging, pathlib
from ignition.service.framework import Service
from ignition.service.infrastructure import InfrastructureDriverCapability
from ignition.model.infrastructure import CreateInfrastructureResponse, DeleteInfrastructureResponse, FindInfrastructureResponse, InfrastructureTask, STATUS_IN_PROGRESS, STATUS_COMPLETE, STATUS_FAILED, STATUS_UNKNOWN
from ignition.model.failure import FAILURE_CODE_RESOURCE_ALREADY_EXISTS, FAILURE_CODE_UNKNOWN, FAILURE_CODE_INTERNAL_ERROR
from kubernetes.client.rest import ApiException

logger = logging.getLogger(__name__)

# class K8sLocationServiceConfigurator():

#     def __init__(self):
#         pass

#     def configure(self, configuration, service_register):
#         service_register.add_service(ServiceRegistration(OpenstackLocationApiService))

class K8sInfrastructureService(Service, InfrastructureDriverCapability):

    def __init__(self, location_translator, tosca_translator):
        self.tosca_translator = tosca_translator
        self.location_translator = location_translator

    def create_infrastructure(self, template, inputs, deployment_location):
        """
        Initiates a request to create infrastructure based on a VNFC package

        :param str template: tosca template of infrastructure to be created
        :param str inputs: values for the inputs defined on the tosca template
        :param dict deployment_location: the valid Openstack location to deploy to
        :return: the id of Infrastructure to be created
        """
        k8s = self.tosca_translator.generate_k8s(template, inputs)

        logger.debug('k8s = {0}'.format(k8s))

        k8s_location = self.location_translator.from_deployment_location(deployment_location)

        infrastructure_id = uuid.uuid4().hex

        k8s_location.create_infrastructure(infrastructure_id, k8s)

        return CreateInfrastructureResponse(infrastructure_id, infrastructure_id)

    def get_infrastructure_task(self, infrastructure_id, request_id, deployment_location):
        """
        Get information about the infrastructure (created or deleted)

        :param str infrastructure_id: identifier of the stack to check
        :param str request_id: identifier of the request to check
        :param dict deployment_location: the Openstack location the infrastructure was deployed to
        :return: a Infrastructure instance describing the status
        """
        k8s_location = self.location_translator.from_deployment_location(deployment_location)
        if k8s_location is None:
            raise ValueError("Invalid deployment location")

        return k8s_location.get_response(infrastructure_id)

    def delete_infrastructure(self, infrastructure_id, deployment_location):
        """
        Remove infrastructure previously created

        :param str infrastructure_id: identifier of the stack to be removed
        :param dict deployment_location: the Openstack location the infrastructure was deployed to
        """
        k8s_location = self.location_translator.from_deployment_location(deployment_location)
        if k8s_location is None:
            raise ValueError("Invalid deployment location")

        k8s_location.delete_infrastructure(infrastructure_id)
        # [k8s_location.delete_pod(name) for name, pod in k8s_location.get_pods(infrastructure_id).items()]
        # [k8s_location.delete_storage(name) for name, storage in k8s_location.get_storage(infrastructure_id).items()]

        return DeleteInfrastructureResponse(infrastructure_id, infrastructure_id)

    def find_infrastructure(self, template, instance_name, deployment_location):
        return FindInfrastructureResponse("1", {})