# Install to Kubernetes

The following guide details how to install the VIM driver into a Kubernetes environment with helm.

## Install Helm Chart

Download and install the chart using the helm CLI:

```
helm install k8s-vim-driver-<version>.tgz --name k8s-vim-driver
```

helm install --name k8s-vim-driver https://github.com/accanto-systems/k8s-vim-driver/releases/download/v0.1.0/k8s-vim-driver-0.1.0.tgz

The above installation will expect Kafka to be running in the same Kubernetes namespace with name `foundation-kafka`, which is the default installed by Stratoss&trade; Lifecycle Manager. If different, override the Kafka address:

```
helm install k8s-vim-driver-<version>.tgz --name k8s-vim-driver --set app.config.override.messaging.connection_address=myhost:myport
```

The driver runs with SSL enabled by default. The installation will generate a self-signed certificate and key by default, adding them to the Kubernetes secret "k8svd-tls". To use a custom certificate and key in your own secret, override the properties under "apps.config.security.ssl.secret".

# Access Swagger UI

The Swagger UI can be found at `http://your_host:31637/api/infrastructure/ui` e.g. `https://localhost:31637/api/infrastructure/ui`
