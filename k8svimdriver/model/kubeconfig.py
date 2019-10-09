import yaml

class KubeConfig():
    def __init__(self, tmppath, name, k8sServer, k8sToken):
        self.tmppath = tmppath
        self.name = name
        # construct kubeconfig file from deployment location properties
        self.kubeConfig = {
            "apiVersion": "v1",
            "clusters": [{
                "name": "mycluster",
                "cluster": {
                    # TODO assume insecure for now
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
        filename = self.tmppath + '/dl_' + self.name + '.yml'
        with open(filename, 'w') as outfile:
            yaml.dump(self.kubeConfig, outfile, default_flow_style=False)
        return filename