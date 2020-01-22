import uuid, yaml, json, sys, threading, logging
from threading import Thread
from kubernetes import client, config, watch
from kubernetes.client.rest import ApiException as K8sApiException
from kubernetes.client import V1DeleteOptions
from ignition.model.infrastructure import InfrastructureTask
from ignition.model.failure import FailureDetails, FAILURE_CODE_INTERNAL_ERROR, FAILURE_CODE_INFRASTRUCTURE_ERROR, FAILURE_CODE_UNKNOWN, FAILURE_CODE_INTERNAL_ERROR, FAILURE_CODE_RESOURCE_NOT_FOUND, FAILURE_CODE_RESOURCE_ALREADY_EXISTS
from ignition.service.framework import Service, Capability, interface
from ignition.service.logging import logging_context, LM_HTTP_HEADER_PREFIX, LM_HTTP_HEADER_TXNID, LM_HTTP_HEADER_PROCESS_ID
from ignition.model.infrastructure import STATUS_IN_PROGRESS, STATUS_UNKNOWN, STATUS_FAILED, STATUS_COMPLETE, InfrastructureTask, CreateInfrastructureResponse
from ignition.api.exceptions import ApiException
from k8svimdriver.k8s.cache import DeploymentLocationCache
from k8svimdriver.model.kubeconfig import KubeConfig

logger = logging.getLogger(__name__)

K8S_SERVER_PROP = 'k8s-server'
K8S_USERNAME = 'k8s-username'
K8S_CERT_AUTH_DATA_PROP = 'k8s-certificate-authority-data'
K8S_CLIENT_CERT_DATA_PROP = 'k8s-client-certificate-data'
K8S_CLIENT_KEY_DATA_PROP = 'k8s-client-key-data'
K8S_TOKEN_PROP = 'k8s-token'
K8S_NAMESPACE = "k8s-namespace"
REGISTRY_URI_PROP = 'registry_uri'

class InvalidDeploymentLocationException(ApiException):
    status_code = 400

class K8sDeploymentLocation():
    def __init__(self, deployment_location, k8s_properties, inf_messaging_service):
        self.k8s_properties = k8s_properties
        self.inf_messaging_service = inf_messaging_service

        logger.debug('deployment location=' + str(deployment_location))

        self.__name = deployment_location.get('name')
        if self.__name is None:
            raise InvalidDeploymentLocationException('Deployment Location managed by the K8s VIM Driver must have a name')

        dl_properties = deployment_location.get('properties', {})
        if dl_properties is None:
            raise InvalidDeploymentLocationException('Deployment Location properties are missing')

        k8sNamespace = dl_properties.get(K8S_NAMESPACE, None)
        if k8sNamespace is None or k8sNamespace == '':
            raise InvalidDeploymentLocationException('Deployment Location managed by the K8s VIM Driver must specify a property value for \'{0}\''.format(K8S_NAMESPACE))
        self.__k8sNamespace = k8sNamespace

        k8sServer = dl_properties.get(K8S_SERVER_PROP, None)
        if k8sServer is None or k8sServer == '':
            raise InvalidDeploymentLocationException('Deployment Location managed by the K8s VIM Driver must specify a property value for \'{0}\''.format(K8S_SERVER_PROP))
        self.__k8sServer = k8sServer

        self.kubeconfig_file = self.createKubeConfig(deployment_location)
        self.k8s_client = config.new_client_from_config(config_file=self.kubeconfig_file)

        self.watcher = watch.Watch()

        self.init_pod_watcher()

    def createKubeConfig(self, deployment_location):
      dl_properties = deployment_location['properties']
      return KubeConfig(self.k8s_properties.tmpdir, deployment_location['name'], dl_properties[K8S_SERVER_PROP], dl_properties.get(K8S_TOKEN_PROP, None), dl_properties.get(K8S_CERT_AUTH_DATA_PROP, None), dl_properties.get(K8S_CLIENT_CERT_DATA_PROP, None), dl_properties.get(K8S_CLIENT_KEY_DATA_PROP, None)).write()

    def init_pod_watcher(self):
        self.pod_watcher = threading.Thread(target=self.pod_watcher_worker, args=())
        self.pod_watcher.setDaemon(True)
        self.pod_watcher.start()

    def pod_watcher_worker(self):
        try:
            logger.info('Monitoring pods')

            # TODO loop until close condition is set
            while True:
                last_seen_version = 0
                # poll forever (timeout == 0)
                for pod_event in self.watcher.stream(self.coreV1Api().list_pod_for_all_namespaces, resource_version=last_seen_version, timeout_seconds=0):
                    event_type = pod_event['type']
                    pod = pod_event['object']
                    metadata = pod.metadata

                    if last_seen_version == 0:
                        # track where we are up to in the pod events stream in case we have to restart
                        last_seen_version = metadata.resource_version

                    pod_name = metadata.name
                    labels = metadata.labels
                    infrastructure_id = labels.get('infrastructure_id', None)
                    if infrastructure_id is not None:
                        logging_context.set_from_dict(labels)
                        try:
                            logger.debug('Got pod event {0}'.format(pod_event))

                            outputs = {}
                            phase = pod.status.phase
                            podStatus = self.__build_pod_status(event_type, pod, outputs)
                            request_type = 'CREATE'
                            failure_details = None
                            outputs = {
                                "host": pod.metadata.name
                            }

                            if phase is None:
                                status = STATUS_UNKNOWN
                            elif phase in ['Pending']:
                                container_statuses = pod.status.container_statuses
                                if container_statuses is not None and len(container_statuses) > 0:
                                    waiting = container_statuses[0].state.waiting
                                    if(waiting is not None):
                                        if(waiting.reason in ['ErrImagePull', 'ImagePullBackOff']):
                                            status = STATUS_FAILED
                                            failure_details = FailureDetails(FAILURE_CODE_INFRASTRUCTURE_ERROR, 'ErrImagePull')
                                        else:
                                            status = STATUS_IN_PROGRESS
                                    else:
                                        status = STATUS_IN_PROGRESS
                                else:
                                    status = STATUS_IN_PROGRESS
                            elif phase in ['Running']:
                                status = STATUS_COMPLETE
                            elif phase in ['Failed']:
                                status = STATUS_FAILED
                                failure_details = FailureDetails(FAILURE_CODE_INFRASTRUCTURE_ERROR, podStatus.status_reason)
                            else:
                                status = STATUS_UNKNOWN

                            if status in [STATUS_COMPLETE, STATUS_FAILED]:
                                if status == STATUS_COMPLETE:
                                    try:
                                        # try to find the ConfigMap that contains information on output property mappings
                                        cm = self.coreV1Api().read_namespaced_config_map(infrastructure_id, self.namespace())
                                        logger.info("Got ConfigMap {0} for infrastructure_id {1}".format(str(cm), infrastructure_id))
                                        if cm is not None:
                                            for output_prop_name, k8s_key in cm.data.items():
                                                logger.info("Output: {0}={1}".format(output_prop_name, k8s_key))
                                                if k8s_key.startswith('network.'):
                                                    k8s_prop_name = k8s_key[len('network.'):]
                                                    logger.info("k8s_prop_name: {0}".format(k8s_prop_name))

                                                annotations = pod.metadata.annotations
                                                networks_status_str = annotations.get('k8s.v1.cni.cncf.io/networks-status', None)
                                                logger.info('networks_status_str: {0}'.format(str(networks_status_str)))
                                                if networks_status_str is not None:
                                                    networks_status = json.loads(networks_status_str)
                                                    for network_status in networks_status:
                                                        net_name = network_status.get('name', None)
                                                        net_ips = network_status.get('ips', {})
                                                        logger.info('net_name {0}, net_ips {1}'.format(net_name, str(net_ips)))
                                                        if net_name is not None and len(net_ips) > 0:
                                                            if net_name == k8s_prop_name:
                                                                outputs[output_prop_name] = net_ips[0]
                                                else:
                                                    logger.info('network status not found for output property {0}'.format(output_prop_name))

                                    except K8sApiException as e:
                                        # ok
                                        if e.status == 404:
                                            logger.info("Unable to find cm for infrastructure id {0}".format(infrastructure_id))

                                inf_task = InfrastructureTask(infrastructure_id, infrastructure_id, status, failure_details, outputs)
                                logger.info('Sending infrastructure response {0}'.format(str(inf_task)))

                                self.inf_messaging_service.send_infrastructure_task(inf_task)
                        finally:
                            logging_context.clear()
        except Exception:
            logger.exception("Unexpected exception watching pods, re-initializing")
            self.pod_watcher_worker()

    def storage_watcher_worker(self):
        logger.debug('Monitoring storage')
        for item in self.watcher.stream(self.coreV1Api().list_persistent_volume, timeout_seconds=0):
            storage = item['object']

            logger.debug('storage event {0}'.format(item))

    def namespace(self):
        return self.__k8sNamespace

    def coreV1Api(self):
        return client.CoreV1Api(self.k8s_client)

    def customApi(self):
        return client.CustomObjectsApi(self.k8s_client)

    def create_infrastructure_impl(self, infrastructure_id, k8s):
        try:
            logger.info('storage=' + str(k8s.get('storage')))

            for storage_name, storage in k8s.get('storage', {}).items():
                storageSize = storage.get('size', None)
                storageClassName = storage.get('storageClassName', None)
                properties = {
                }
                if storageClassName == "hostpath":
                    properties['hostpath'] = storage.get('hostpath', None)

                self.create_storage(storage_name, storageSize, storageClassName, infrastructure_id, properties)

            for _, network in k8s.get('networks', {}).items():
                network_name = network.get('name', None)
                bridge = network.get('bridge', None)
                subnet = network.get('subnet', None)
                range_start = network.get('range_start', None)
                range_end = network.get('range_end', None)
                self.create_network(infrastructure_id, network_name, bridge, subnet, range_start, range_end)

            # TODO mapping storageClassName to pods - just have one storage class?
            for pod in k8s.get('pods', []):
                pod_name = pod.get('name', None)
                image = pod.get('image', None)
                container_port = pod.get('container_port', None)
                # storage_name, storageClassName, storageSize
                storage = pod.get('storage', [])
                networks = pod.get('network', [])
                logger.info('pod_name=' + pod_name)
                self.create_pod(pod_name, image, container_port, infrastructure_id, storage, networks)

            self.create_config_map_for_outputs(pod_name, infrastructure_id, k8s.get('outputs', {}))
        except K8sApiException as e:
            if e.status == 409:
                logger.error('K8s exception1' + str(e))
                self.inf_messaging_service.send_infrastructure_task(InfrastructureTask(infrastructure_id, infrastructure_id, STATUS_FAILED, FailureDetails(FAILURE_CODE_RESOURCE_ALREADY_EXISTS, "Resource already exists"), {}))
            else:
                logger.error('K8s exception2' + str(e))
                self.inf_messaging_service.send_infrastructure_task(InfrastructureTask(infrastructure_id, infrastructure_id, STATUS_FAILED, FailureDetails(FAILURE_CODE_INTERNAL_ERROR, str(e)), {}))
        except Exception as e:
            logger.error('K8s exception2' + str(e))
            self.inf_messaging_service.send_infrastructure_task(InfrastructureTask(infrastructure_id, infrastructure_id, STATUS_FAILED, FailureDetails(FAILURE_CODE_INTERNAL_ERROR, str(e)), {}))

    def create_infrastructure(self, infrastructure_id, k8s):
        # Run in a thread so the driver can respond ASAP
        # TODO use Ignition job queue to queue these requests up
        worker = Thread(target=self.create_infrastructure_impl, args=(infrastructure_id, k8s,))
        # force the driver to wait for any create infrastructure threads to finish before exiting
        worker.setDaemon(False)
        worker.start()

        return CreateInfrastructureResponse(infrastructure_id, infrastructure_id)

    def create_config_map_for_outputs(self, pod_name, infrastructure_id, outputs):
        logger.info("output = {0}".format(str(outputs)))
        logger.info("output type = {0}".format(str(type(outputs))))
        api_response = self.coreV1Api().create_namespaced_config_map(namespace=self.namespace(), body=client.V1ConfigMap(api_version="v1",
            kind="ConfigMap",
            metadata=client.V1ObjectMeta(
                namespace=self.namespace(),
                name=infrastructure_id,
                labels={"infrastructure_id": infrastructure_id}),
            data=outputs)
        )

        # TODO handle api_response

        logger.info("Config Map created. status='%s'" % str(api_response))

    def normalize_name(self, name):
        return name.replace("_", "-")

    def create_pod_object(self, podName, image, container_port, infrastructure_id, storage, networks):
        # Configure Pod template container
        ports = []
        if(container_port is not None):
            ports.append(client.V1ContainerPort(name="http", container_port=container_port, protocol="TCP"))

        volumes = []
        volumeMounts = []
        for s in storage:
            volumes.append(client.V1Volume(
                name=self.normalize_name(s["name"]),
                persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(
                    claim_name=self.normalize_name(s["name"])
                )
            ))
            volumeMounts.append(client.V1VolumeMount(
                name=self.normalize_name(s["name"]),
                mount_path=s["mountPath"]
                # other optional arguments, see the volume mount doc link below
            ))

        container = client.V1Container(
            name=podName,
            image=image,
            image_pull_policy="IfNotPresent",
            ports=ports,
            volume_mounts=volumeMounts)

        networks_as_string = ', '.join(list(map(lambda network: network['name'], networks)))
        logger.info('pod networks: ' + str(networks_as_string))
        spec = client.V1PodSpec(
            containers=[container],
            volumes=volumes)
        return client.V1Pod(
            api_version="v1",
            kind="Pod",
            metadata=client.V1ObjectMeta(name=podName, labels={
                "infrastructure_id": infrastructure_id,
                LM_HTTP_HEADER_TXNID: logging_context.get(LM_HTTP_HEADER_TXNID, ""),
                LM_HTTP_HEADER_PROCESS_ID: logging_context.get(LM_HTTP_HEADER_PROCESS_ID, "")
            },
            annotations={
                "k8s.v1.cni.cncf.io/networks": networks_as_string,
            }),
            spec=spec)

    def create_network(self, infrastructure_id, name, bridge, subnet, range_start, range_end):
        logger.info("Creating network {0} {1} {2} {3} {4} {5}".format(infrastructure_id, name, bridge, subnet, range_start, range_end))

        # we support Multus networks only at present
        config = {
            "name": name,
            "type": "bridge",
            "bridge": bridge,
            "isDefaultGateway": True,
            "forceAddress": False,
            "ipMasq": True,
            "hairpinMode": True,
            "ipam": {
                "type": "host-local",
                "subnet": subnet,
                "rangeStart": range_start,
                "rangeEnd": range_end
            }
        }

        body = {
            "apiVersion": "k8s.cni.cncf.io/v1",
            "kind": "NetworkAttachmentDefinition",
            "metadata": {
                "name": name,
                "labels": {
                    "infrastructure_id": infrastructure_id
                }
            },
            "spec": {
                "config": json.dumps(config)
            }
        }

        logger.info('create network, body = {0}'.format(json.dumps(body)))
        try:
            self.customApi().create_namespaced_custom_object(group="k8s.cni.cncf.io", version="v1", namespace=self.namespace(), plural="network-attachment-definitions", body=body)
        except K8sApiException as e:
            if e.reason == 'Conflict':
                # this is ok, assume the network already exists
                pass
            else:
                raise

    def create_pod(self, podName, image, container_port, infrastructure_id, storage, networks):
        logger.info("pod storage="+str(storage))
        for s in storage:
            claimObject = client.V1PersistentVolumeClaim(
                metadata=client.V1ObjectMeta(
                    namespace=self.namespace(),
                    name=self.normalize_name(s["name"]),
                    labels={"infrastructure_id": infrastructure_id}),
                spec=client.V1PersistentVolumeClaimSpec(
                    access_modes=["ReadWriteOnce"],
                    resources=client.V1ResourceRequirements(
                        requests={
                            "storage": s["size"]
                        },
                        limits={
                        }
                    ),
                    # TODO
                    storage_class_name=s["storageClassName"]
                )
            )

            logger.info("Volume claim %s" % str(claimObject))

            api_response = self.coreV1Api().create_namespaced_persistent_volume_claim(
                body=claimObject,
                namespace=self.namespace())

            # TODO handle api_response

            logger.info("Persistent volume claim created. status='%s'" % str(api_response.status))

        logger.info('Creating pod object')
        pod = self.create_pod_object(podName, image, container_port, infrastructure_id, storage, networks)
        logger.info("Namespace = " + self.namespace())
        logger.info("Creating pod %s" % str(pod))

        # Create pod
        api_response = self.coreV1Api().create_namespaced_pod(
            body=pod,
            namespace=self.namespace())

        logger.info("Pod created. status='%s'" % str(api_response.status))

        return api_response

    def __build_pod_status(self, request_type, pod, outputs):
        phase = pod.status.phase
        status_reason = None
        status = STATUS_UNKNOWN

        # if request_type == 'CREATE':
        if(phase is None):
            status = STATUS_UNKNOWN
        elif(phase in ['Pending']):
            container_statuses = pod.status.container_statuses
            if container_statuses is not None and len(container_statuses) > 0:
                waiting = container_statuses[0].state.waiting
                if(waiting is not None):
                    if(waiting.reason == 'ErrImagePull'):
                        status = STATUS_FAILED
                        status_reason = 'ErrImagePull'
                    else:
                        status = STATUS_IN_PROGRESS
                else:
                    status = STATUS_IN_PROGRESS
            else:
                status = STATUS_IN_PROGRESS
        elif(phase in ['Running']):
            status = STATUS_COMPLETE
        elif(phase in ['Failed']):
            status = STATUS_FAILED
        else:
            status = STATUS_UNKNOWN
        return {
          'status': status,
          'status_reason': status_reason
        }

    def __build_pvc_status(self, request_type, pvc, outputs):
        phase = pvc.status.phase
        status_reason = None
        status = STATUS_UNKNOWN

        logger.debug('__build_pvc_status {0} {1}'.format(request_type, pvc))

        if(phase is None):
            status = STATUS_UNKNOWN
        elif(phase == 'Failed'):
            status = STATUS_FAILED
        elif(phase == 'Bound'):
            status = STATUS_COMPLETE
        elif(phase == 'Available'):
            # TODO check this
            status = STATUS_IN_PROGRESS
        else:
            status = STATUS_UNKNOWN

        return {
          'status': status,
          'status_reason': status_reason
        }

    def get_infrastructure(self, infrastructure_id, request_type):
        outputs = {}

        statuses = []
        statuses.append(list(map(lambda pod: self.__build_pod_status(request_type, pod, outputs), self.coreV1Api().list_namespaced_pod(namespace=self.namespace(), label_selector='infrastructure_id={}'.format(infrastructure_id)))))
        statuses.append(list(map(lambda pvc: self.__build_pvc_status(request_type, pvc, outputs), self.coreV1Api().list_namespaced_persistent_volume_claim(namespace=self.namespace(), label_selector='infrastructure_id={}'.format(infrastructure_id)))))

        failure_details = None
        status = STATUS_COMPLETE

        if request_type == 'CREATE':
            failed = list(filter(lambda x: x['status'] == STATUS_FAILED, statuses))
            if len(failed) > 0:
                status = STATUS_FAILED
                failure_details = FailureDetails(FAILURE_CODE_INFRASTRUCTURE_ERROR, failed[0].status_reason)

            in_progress = list(filter(lambda x: x['status'] == STATUS_IN_PROGRESS, statuses))
            if len(in_progress) > 0:
                status = STATUS_IN_PROGRESS

            return InfrastructureTask(infrastructure_id, infrastructure_id, status, failure_details, outputs)
        elif request_type == 'DELETE':
            failed = list(filter(lambda x: x['status'] == STATUS_FAILED, statuses))
            in_progress = list(filter(lambda x: x['status'] == STATUS_IN_PROGRESS, statuses))
            if len(failed) > 0:
                status = STATUS_FAILED
                failure_details = FailureDetails(FAILURE_CODE_INFRASTRUCTURE_ERROR, failed[0].status_reason)
            elif len(in_progress) > 0 or len(statuses) > 0:
                status = STATUS_IN_PROGRESS

            return InfrastructureTask(infrastructure_id, infrastructure_id, status, failure_details, outputs)
        else:
            raise ValueError("Invalud request_type {0}".format(request_type)) 

    def delete_infrastructure(self, infrastructure_id):
        self.delete_pod_with_infrastructure_id(infrastructure_id)
        self.delete_storage_with_infrastructure_id(infrastructure_id)
        self.delete_networks_with_infrastructure_id(infrastructure_id)

    def delete_pod_with_infrastructure_id(self, infrastructure_id):
        v1 = self.coreV1Api()
        pod_list = v1.list_namespaced_pod(namespace=self.namespace(), label_selector='infrastructure_id={}'.format(infrastructure_id))
        logger.info('delete_pod_with_infrastructure_id {0}'.format(str(pod_list)))
        if(len(pod_list.items)) > 0:
            name = pod_list.items[0].metadata.name
            logger.info('Deleting pod with name {0} in namespace {1}'.format(name, self.namespace()))
            v1.delete_namespaced_pod(namespace=self.namespace(), name=name)

    def delete_pod(self, name):
        api_response = self.coreV1Api().delete_namespaced_pod(namespace=self.namespace(), name=name)

    # capacity: 1Gb
    def create_storage(self, name, capacity, storageClassName, infrastructure_id, properties):
        v1 = self.coreV1Api()

        logger.debug('storageClassName=' + storageClassName)

        if(storageClassName == 'hostpath'):
            hostpath = properties.get('hostpath', None)
            if(hostpath is None):
                raise ValueError("Hostpath property must be provided") 

            spec=client.V1PersistentVolumeSpec(
                capacity={'storage': capacity},
                access_modes=['ReadWriteOnce'],
                host_path=client.V1HostPathVolumeSource(
                    path=hostpath,
                    type=''
                ))

            storage = client.V1PersistentVolume(
                api_version='v1',
                kind='PersistentVolume',
                metadata=client.V1ObjectMeta(name=name, labels={"infrastructure_id": infrastructure_id}),
                spec=spec)

            logger.debug("Creating storage %s" % str(storage))

            api_response = v1.create_persistent_volume(storage)

            logger.debug("Storage created. status='%s'" % str(api_response.status))
        else:
            # the storage provisioner will create the persistent volume in this case
            pass

    def get_storage(self, infrastructure_id):
        v1 = self.coreV1Api()
        storage_list = v1.list_persistent_volume(label_selector='infrastructure_id={}'.format(infrastructure_id))
        if(len(storage_list.items)) > 0:
            name = storage_list.items[0].metadata.name
            return v1.read_persistent_volume(name=name)
        else:
            return None

    def delete_networks_with_infrastructure_id(self, infrastructure_id):
        customApi = self.customApi()
        network_list = customApi.list_namespaced_custom_object(group="k8s.cni.cncf.io", version="v1", namespace=self.namespace(), plural="network-attachment-definitions", label_selector='infrastructure_id={}'.format(infrastructure_id), watch=False)
        for network in network_list['items']:
            print('Deleting network='+str(network))
            # TODO handle errors
            api_response = customApi.delete_namespaced_custom_object(group="k8s.cni.cncf.io", version="v1", namespace=self.namespace(), plural="network-attachment-definitions", name=network['metadata']['name'], body=V1DeleteOptions())

    def delete_storage_with_infrastructure_id(self, infrastructure_id):
        v1 = self.coreV1Api()
        storage_list = v1.list_namespaced_persistent_volume_claim(namespace=self.namespace(), label_selector='infrastructure_id={}'.format(infrastructure_id))
        for storage in storage_list.items:
            # TODO handle errors
            api_response = v1.delete_namespaced_persistent_volume_claim(namespace=self.namespace(), name=storage.metadata.name)

    def delete_storage(self, name):
        api_response = self.coreV1Api().delete_persistent_volume(name=name)

class DeploymentLocationTranslatorCapability(Capability):
    @interface
    def from_deployment_location(self, deployment_location):
        pass

class K8sDeploymentLocationTranslator(Service, DeploymentLocationTranslatorCapability):
    def __init__(self, k8s_properties, **kwargs):
        self.dl_cache = DeploymentLocationCache()
        self.k8s_properties = k8s_properties
        if 'inf_messaging_service' not in kwargs:
            raise ValueError('inf_messaging_service argument not provided')
        self.inf_messaging_service = kwargs.get('inf_messaging_service')

    def from_deployment_location(self, deployment_location):
        dl_name = deployment_location.get('name', None)
        if dl_name is None:
            raise ValueError('Deployment Location managed by the K8s VIM Driver must have a name')

        dl = self.dl_cache.get(dl_name)
        if dl is None:
            dl = K8sDeploymentLocation(deployment_location, self.k8s_properties, self.inf_messaging_service)
            self.dl_cache.put(dl_name, dl)

        return dl
