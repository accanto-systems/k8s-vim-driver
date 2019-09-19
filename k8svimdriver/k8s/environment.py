import uuid, yaml, json, sys, threading, logging
from k8svimdriver.k8s.cache import K8sCache, DeploymentLocationCache
from kubernetes import client, config, watch
from kubernetes.client.rest import ApiException
from k8svimdriver.service.cache import ResponseCache
from ignition.model.infrastructure import InfrastructureTask
from ignition.model.failure import FailureDetails, FAILURE_CODE_INTERNAL_ERROR, FAILURE_CODE_INFRASTRUCTURE_ERROR, FAILURE_CODE_UNKNOWN, FAILURE_CODE_INTERNAL_ERROR, FAILURE_CODE_RESOURCE_NOT_FOUND, FAILURE_CODE_RESOURCE_ALREADY_EXISTS
from k8svimdriver.model.kubeconfig import KubeConfig

logger = logging.getLogger(__name__)

K8S_SERVER_PROP = 'k8s-server'
K8_USERNAME = 'k8s-username'
K8_CERT_AUTH_DATA_PROP = 'certificate-authority-data'
K8_CLIENT_CERT_DATA_PROP = 'client-certificate-data'
K8_CLIENT_KEY_DATA_PROP = 'client-key-data'
K8S_TOKEN_PROP = 'k8s-token'
K8S_NAMESPACE = "k8s-namespace"
REGISTRY_URI_PROP = 'registry_uri'

class K8sDeploymentLocation():
    def __init__(self, deployment_location):
        # def __init__(self, name, k8sServer, certificateAuthorityData, clientCertificateData, clientKeyData, username):
        self.__name = deployment_location.get('name')
        if self.__name is None:
            raise ValueError('Deployment Location managed by the K8s VIM Driver must have a name')

        dl_properties = deployment_location.get('properties', {})
        if dl_properties is None:
            raise ValueError('Deployment Location properties are missing')

        k8sNamespace = dl_properties.get(K8S_NAMESPACE, None)
        if k8sNamespace is None or k8sNamespace == '':
            raise ValueError('Deployment Location managed by the K8s VIM Driver must specify a property value for \'{0}\''.format(K8S_NAMESPACE))
        self.__k8sNamespace = k8sNamespace

        k8sServer = dl_properties.get(K8S_SERVER_PROP, None)
        if k8sServer is None or k8sServer == '':
            raise ValueError('Deployment Location managed by the K8s VIM Driver must specify a property value for \'{0}\''.format(K8S_SERVER_PROP))
        self.__k8sServer = k8sServer

        config_file = self.createKubeConfig(deployment_location)
        self.k8s_client = config.new_client_from_config(config_file=config_file)

        self.watcher = watch.Watch()
        self.k8s_cache = K8sCache()

        self.responses = ResponseCache()

        self.pod_watcher = threading.Thread(target=self.pod_watcher_worker, args=())
        self.pod_watcher.setDaemon(True)
        self.pod_watcher.start()

        self.storage_watcher = threading.Thread(target=self.storage_watcher_worker, args=())
        self.storage_watcher.setDaemon(True)
        self.storage_watcher.start()

    def createKubeConfig(self, deployment_location):
      dl_properties = deployment_location['properties']
      return KubeConfig(deployment_location['name'], dl_properties[K8S_SERVER_PROP], dl_properties[K8S_TOKEN_PROP]).write()

    def pod_watcher_worker(self):
        logger.debug('Monitoring pods')
        for item in self.watcher.stream(self.coreV1Api().list_pod_for_all_namespaces, timeout_seconds=0):
            pod = item['object']

            # logger.info('pod event {0}'.format(item))

            pod_name = pod.metadata.name
            labels = pod.metadata.labels
            infrastructure_id = labels.get('infrastructure_id', None)
            if infrastructure_id is not None:
                self.responses.update_pod(infrastructure_id, item['type'], pod)

    def storage_watcher_worker(self):
        logger.debug('Monitoring storage')
        for item in self.watcher.stream(self.coreV1Api().list_persistent_volume, timeout_seconds=0):
            storage = item['object']

            # logger.info('storage event {0}'.format(item))

            storage_name = storage.metadata.name
            labels = storage.metadata.labels
            if labels is not None:
                infrastructure_id = labels.get('infrastructure_id', None)
                if(infrastructure_id is not None):
                    self.responses.update_storage(infrastructure_id, item['type'], storage)
            else:
                pass
                # logger.info("Unable to find labels on storage %s" % str(storage))

    def get_response(self, infrastructure_id):
        return self.responses.get_response(infrastructure_id)

    def namespace(self):
        return self.__k8sNamespace

    def coreV1Api(self):
        return client.CoreV1Api(self.k8s_client)

    def create_infrastructure(self, infrastructure_id, k8s):
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

            # TODO mapping storageClassName to pods - just have one storage class?
            for pod in k8s.get('pods', []):
                pod_name = pod.get('name', None)
                image = pod.get('image', None)
                container_port = pod.get('container_port', None)
                # storage_name, storageClassName, storageSize
                storage = pod.get('storage', [])
                logger.info('pod_name=' + pod_name)
                self.create_pod(pod_name, image, container_port, infrastructure_id, storage)
        except ApiException as e:
            if e.status == 409:
                self.responses.update_response(InfrastructureTask(infrastructure_id, infrastructure_id, FAILURE_CODE_RESOURCE_ALREADY_EXISTS, None, {}))
            else:
                self.responses.update_response(InfrastructureTask(infrastructure_id, infrastructure_id, FAILURE_CODE_INTERNAL_ERROR, FailureDetails(FAILURE_CODE_INTERNAL_ERROR, str(e)), {}))
        except Exception as e:
            self.responses.update_response(InfrastructureTask(infrastructure_id, infrastructure_id, FAILURE_CODE_INTERNAL_ERROR, FailureDetails(FAILURE_CODE_INTERNAL_ERROR, str(e)), {}))

    # def create_pod_object(self, podName, image, container_port, infrastructure_id, storage_name, storageClassName):
    def create_pod_object(self, podName, image, container_port, infrastructure_id, storage):
        # Configure Pod template container
        ports = []
        if(container_port is not None):
            ports.append(client.V1ContainerPort(container_port=container_port))

        volumes = []
        volumeMounts = []
        for s in storage:
            volumes.append(client.V1Volume(
                name=s["name"],
                persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(
                    claim_name=s["name"]
                )
            ))
            volumeMounts.append(client.V1VolumeMount(
                name=s["name"],
                mount_path=s["mountPath"]
                # other optional arguments, see the volume mount doc link below
            ))

        container = client.V1Container(
            name=podName,
            image=image,
            ports=ports,
            volume_mounts=volumeMounts)

        spec = client.V1PodSpec(
            containers=[container],
            volumes=volumes)
        return client.V1Pod(
            api_version="v1",
            kind="Pod",
            metadata=client.V1ObjectMeta(name=podName, labels={"infrastructure_id": infrastructure_id}),
            spec=spec)

    # storage_name, storageClassName, storageCapacity
    def create_pod(self, podName, image, container_port, infrastructure_id, storage):
        logger.info("pod storage="+str(storage))
        for s in storage:
            claimObject = client.V1PersistentVolumeClaim(
                metadata=client.V1ObjectMeta(name=s["name"], labels={"infrastructure_id": infrastructure_id}),
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
        pod = self.create_pod_object(podName, image, container_port, infrastructure_id, storage)
        logger.info("Namespace = " + self.namespace())
        logger.info("Creating pod %s" % str(pod))

        # Create pod
        api_response = self.coreV1Api().create_namespaced_pod(
            body=pod,
            namespace=self.namespace())

        logger.info("Pod created. status='%s'" % str(api_response.status))

        return api_response

    def delete_infrastructure(self, infrastructure_id):
        # response = self.get_response(infrastructure_id)
        # pods = response['pods']
        # [self.delete_pod(infrastructure_id) for pod in pods]

        self.delete_pod_with_infrastructure_id(infrastructure_id)
        self.delete_storage_with_infrastructure_id(infrastructure_id)

    def delete_pod_with_infrastructure_id(self, infrastructure_id):
        v1 = self.coreV1Api()
        pod_list = v1.list_namespaced_pod(namespace=self.namespace(), label_selector='infrastructure_id={}'.format(infrastructure_id))
        if(len(pod_list.items)) > 0:
            name = pod_list.items[0].metadata.name
            v1.delete_namespaced_pod(namespace=self.namespace(), name=name)

    def delete_pod(self, name):
        api_response = self.coreV1Api().delete_namespaced_pod(namespace=self.namespace(), name=name)

    def get_pod(self, infrastructure_id):
        pod = self.k8s_cache.getPod(infrastructure_id)
        if(pod is None):
            pod_list = self.coreV1Api().list_namespaced_pod(namespace=self.namespace(), label_selector='infrastructure_id={}'.format(infrastructure_id))
            if(len(pod_list.items)) > 0:
                name = pod_list.items[0].metadata.name
                pod = self.coreV1Api().read_namespaced_pod(namespace=self.namespace(), name=name)
            else:
                pod = None

        return pod

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

    def delete_storage_with_infrastructure_id(self, infrastructure_id):
        v1 = self.coreV1Api()
        storage_list = v1.list_namespaced_persistent_volume_claim(namespace=self.namespace(), label_selector='infrastructure_id={}'.format(infrastructure_id))
        for storage in storage_list:
            api_response = v1.delete_namespaced_persistent_volume_claim(namespace=self.namespace(), name=storage.metadata.name)

    def delete_storage(self, name):
        api_response = self.coreV1Api().delete_persistent_volume(name=name)

class K8sDeploymentLocationTranslator():
    def __init__(self):
        self.dl_cache = DeploymentLocationCache()

    def from_deployment_location(self, deployment_location):
        dl_name = deployment_location.get('name', None)
        if dl_name is None:
            raise ValueError('Deployment Location managed by the K8s VIM Driver must have a name')

        dl = self.dl_cache.get(dl_name)
        if dl is None:
            dl =  K8sDeploymentLocation(deployment_location)
            self.dl_cache.put(dl_name, dl)

        return dl
