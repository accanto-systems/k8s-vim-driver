import yaml

# class KubeCluster():
#     def __init__(self, server):
#         self.insecure-skip-tls-verify = 'true'
#         self.server = server
        
class KubeConfig():
    def __init__(self, name, k8sServer, k8sToken):
        self.name = name
        self.kubeConfig = {
            "apiVersion": "v1",
            "clusters": [{
                "name": "mycluster",
                "cluster": {
                    "insecure-skip-tls-verify": True,
                    "server": k8sServer
                }
            }],
            "contexts": [{
                "name": "mycluster-context",
                "context": {
                    "cluster": "mycluster",
                    "user": "ald-user"
                }
            }],
            "current-context": "mycluster-context",
            "kind": "Config",
            "preferences": {},
            "users": [{
                "name": "ald-user",
                "user": {
                    "token": k8sToken
                }
            }]
        }

    def write(self):
        filename = '/var/k8svd/dl_' + self.name + '.yml'
        # filename = './dl_' + self.name + '.yml'
        with open(filename, 'w') as outfile:
            yaml.dump(self.kubeConfig, outfile, default_flow_style=False)
        return filename