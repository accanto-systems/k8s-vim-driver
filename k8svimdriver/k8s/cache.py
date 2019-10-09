from cachetools import cached, TTLCache  # 1 - let's import the "cached" decorator and the "TTLCache" object from cachetools
from common_cache import Cache

# this is more like a 
class DeploymentLocationCache(object):

    def __init__(self):
        self.cache = {}

    def put(self, name, dl):
        self.cache[name] = dl

    def get(self, name):
        return self.cache.get(name, None)

