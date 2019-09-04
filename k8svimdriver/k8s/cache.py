from cachetools import cached, TTLCache  # 1 - let's import the "cached" decorator and the "TTLCache" object from cachetools
from common_cache import Cache

class K8sCache(object):

    def __init__(self):
        self.podCache = Cache(expire=10)
        self.storageCache = Cache(expire=10)

    def updatePod(self, infrastructure_id, pod):
        self.podCache[infrastructure_id] = pod

    def getPod(self, infrastructure_id):
        return self.podCache[infrastructure_id]

    def updateStorage(self, infrastructure_id, storage):
        self.storageCache[infrastructure_id] = storage

    def getStorage(self, infrastructure_id):
        return self.storageCache[infrastructure_id]

class DeploymentLocationCache(object):

    def __init__(self):
        self.cache = {}

    def put(self, name, dl):
        self.cache[name] = dl

    def get(self, name):
        return self.cache.get(name, None)

