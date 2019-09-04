import logging
import functools
from common_cache import Cache
from ignition.model.infrastructure import STATUS_IN_PROGRESS, STATUS_UNKNOWN, STATUS_FAILED, STATUS_COMPLETE, InfrastructureTask

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# TODO external configuration
CACHE_EXPIRY = 300 # in seconds
MAX_CACHE_CAPACITY = 4096

class ResponseCache(object):
    def __init__(self):
      self.cache = {
      }
      #Cache(capacity=MAX_CACHE_CAPACITY, expire=CACHE_EXPIRY)

    def get_or_create_response(self, infrastructure_id):
      response = self.cache.get(infrastructure_id, None)
      if response is None:
        response = {
          'pods': {
          },
          'storage': {
          }
        }
        self.cache[infrastructure_id] = response
      return response

    def update_pod(self, infrastructure_id, event_type, pod):
      pod_name = pod.metadata.name
      labels = pod.metadata.labels

      response = self.get_or_create_response(infrastructure_id)

      outputs = {}
      pod_response = self.__build_pod_response(event_type, pod, outputs)
      logger.info('update_pod: {0} {1} {2}'.format(infrastructure_id, pod.metadata.name, pod_response))
      response['pods'][pod.metadata.name] = pod_response

    def __build_pod_response(self, event_type, pod, outputs):
        phase = pod.status.phase
        status_reason = None
        status = STATUS_UNKNOWN

        # logger.info('__build_pod_response {0} {1}'.format(event_type, pod))

        if event_type in ['ADDED', 'MODIFIED']:
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

        elif event_type == 'DELETED':
          if(phase is None):
              status = STATUS_UNKNOWN
          elif(phase in ['Pending']):
            # container_statuses = pod.status.containerStatuses
            # if(len(container_statuses) > 0):
            #     waiting = container_statuses[0].state.get('waiting', None)
            #     if(waiting is not None):
            #         if(waiting.reason == 'ErrImagePull'):
            #           status = STATUS_FAILED
            #           status_reason = stack_status.get('stack_status_reason', None)
            # else:
              status = STATUS_IN_PROGRESS
          elif(phase in ['Running']):
              status = STATUS_COMPLETE
          elif(phase in ['Failed']):
              status = STATUS_FAILED
          else:
              status = STATUS_UNKNOWN

        else:
          logger.warn('Unhandled event {0} {1}'.format(event_type, pod))

        return {
          'status': status,
          'status_reason': status_reason
        }

    def update_response(self, infrastructure_task):
      infrastructure_id = infrastructure_task.infrastructure_id
      response = self.get_or_create_response(infrastructure_id)
      response['response'] = infrastructure_task

    def update_storage(self, infrastructure_id, event_type, storage):
      response = self.get_or_create_response(infrastructure_id)

      logger.info('update_storage: ' + str(response))

      outputs = {}
      response['storage'][storage.metadata.name] = self.__build_storage_response(storage, outputs)

    def get_response(self, infrastructure_id):
      response = self.cache.get(infrastructure_id, None)

      outputs = {}
      status_reason = None

      if response is not None:
        ret = response.get('response', None)
        if ret is None:
          objects = [pod for name, pod in response['pods'].items()] + [storage for name, storage in response['storage'].items()]
          status = functools.reduce(lambda object_a, object_b : self.reduce(object_a, object_b), objects)
          ret = InfrastructureTask(infrastructure_id, infrastructure_id, status, status_reason, outputs)
      else:
        status = STATUS_IN_PROGRESS
        ret = InfrastructureTask(infrastructure_id, infrastructure_id, status, status_reason, outputs)

      return ret

    def get_pods(self, infrastructure_id):
      response = self.cache.get(infrastructure_id, None)
      ret = []

      if response is not None:
        ret = response['pods']

      return ret

    def get_storage(self, infrastructure_id):
      response = self.cache.get(infrastructure_id, None)
      ret = []

      if response is not None:
        ret = response['storage']

      return ret


    def reduce(self, object_a, object_b):
        if object_a['status'] == STATUS_FAILED or object_b['status'] == STATUS_FAILED:
          return STATUS_FAILED
        elif object_a['status'] == STATUS_IN_PROGRESS or object_b['status'] == STATUS_IN_PROGRESS:
          return STATUS_IN_PROGRESS
        elif object_a['status'] == STATUS_UNKNOWN or object_b['status'] == STATUS_UNKNOWN:
          return STATUS_UNKNOWN
        else:
          return STATUS_COMPLETE

    def __build_storage_response(self, pv, outputs):
        phase = pv.status.phase
        logger.info('pv status {0}'.format(phase))
        status_reason = None
        if(phase is None):
            status = STATUS_UNKNOWN
        elif(phase in ['Available', 'Bound']):
            status = STATUS_COMPLETE
        else:
            status = STATUS_UNKNOWN
        return {
          'status': status
        }

    def remove(self, infrastructure_id):
      del self.cache[infrastructure_id]

    def close(self):
      self.cache.shutdown_thread_pool()
