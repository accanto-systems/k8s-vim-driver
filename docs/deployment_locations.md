# Deployment Locations

The deployment location is defined by the following properties:

* k8s-server: the K8s master API e.g. http://10.220.217.248:8080 (microk8s)
* k8s-username: the K8s admin username e.g. "admin" (microk8s)
* certificate-authority-data: certificate (from kubeconfig file)
* client-certificate-data: client certificate (from kubeconfig file)
* client-key-data: client key (from kubeconfig file)
* token: access token (from kubeconfig file)

For MicroK8s, only k8s-server and k8s-username need be specified. For kubeadm, specify either "k8s-username" and either "token" or "certificate-authority-data", "client-certificate-data" and "client-key-data" (all can be taken from the kubeconfig file).

{
    "name": "winterfell",
    "type": "Kubernetes",
    "properties": {
        "k8s-server": "10.220.217.113:8080",
        "k8s-token": "ZXlKaGJHY2lPaUpTVXpJMU5pSXNJbXRwWkNJNklpSjkuZXlKcGMzTWlPaUpyZFdKbGNtNWxkR1Z6TDNObGNuWnBZMlZoWTJOdmRXNTBJaXdpYTNWaVpYSnVaWFJsY3k1cGJ5OXpaWEoyYVdObFlXTmpiM1Z1ZEM5dVlXMWxjM0JoWTJVaU9pSmtaV1poZFd4MElpd2lhM1ZpWlhKdVpYUmxjeTVwYnk5elpYSjJhV05sWVdOamIzVnVkQzl6WldOeVpYUXVibUZ0WlNJNklteHRMWFJ2YTJWdUxXMTJORGxuSWl3aWEzVmlaWEp1WlhSbGN5NXBieTl6WlhKMmFXTmxZV05qYjNWdWRDOXpaWEoyYVdObExXRmpZMjkxYm5RdWJtRnRaU0k2SW14dElpd2lhM1ZpWlhKdVpYUmxjeTVwYnk5elpYSjJhV05sWVdOamIzVnVkQzl6WlhKMmFXTmxMV0ZqWTI5MWJuUXVkV2xrSWpvaU1qUTRNR1l6Wm1VdFpHRmpZaTB4TVdVNUxXSm1aREl0TURBMU1EVTJPVFUxWlRCbUlpd2ljM1ZpSWpvaWMzbHpkR1Z0T25ObGNuWnBZMlZoWTJOdmRXNTBPbVJsWm1GMWJIUTZiRzBpZlEuSEVoNlgyZzdKZ0NOVV8zNHR6ZkRQd1VJeF9Vbi1kRW9teTI2QUdTMmtlUXY1dmE2YVVFZk9Nc1BpcUJnckJpSF9BUkdTYkpiekVlcGhyYVZVc1JfY2JBOTdkSTVIZ25LZTBVY2ZnZnBwbnRTZDZnNTQ5d2dPMGJUMXg1dHBFdGo1NFg2cWpOZ08zd3JPRXp6TEFsLUN4WFpXSDFVanhzNFhsMFBOYXlKd2FBSWYxeldnZmxROG5GZmgyQWV6NWFKUjZYMjZCQTU4cDlHM1ZRVkliaWc2MUxUWXhMUEptSF9mZ2QwdHpkblV5dG1TckZQd2tiUDlnN0stR1ZPVFhqbXNMdGdSYmRWMlVjbGx2YXl4THR3LTB4NnlnQi0zU3piN3diV0hmZGk1WnFxU3VOSHBXVEJvZEwta0N1bTl4ZWJyOG5RVG15Y3ZGdDlhdkQyckdVbkN3",
        "k8s-namespace": "default"
    }
}