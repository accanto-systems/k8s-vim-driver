# Deployment Locations

The deployment location is defined by the following properties:

* k8s-server: the K8s master API e.g. http://10.220.217.248:8080 (microk8s)
* k8s-username: the K8s admin username e.g. "admin" (microk8s)
* certificate-authority-data: certificate (from kubeconfig file)
* client-certificate-data: client certificate (from kubeconfig file)
* client-key-data: client key (from kubeconfig file)
* token: access token (from kubeconfig file)

For MicroK8s, only k8s-server and k8s-username need be specified. For kubeadm, specify either "k8s-username" and either "token" or "certificate-authority-data", "client-certificate-data" and "client-key-data" (all can be taken from the kubeconfig file).