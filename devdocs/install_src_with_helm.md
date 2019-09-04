# Run Helm Chart

You will need:

- Python
- Docker
- Helm

## Build Docker Image

To build the Docker image for the driver from this repository, do the following:

1. Build a python whl for the driver

```
python3 setup.py bdist_wheel
```

2. Move the whl now in `dist` to the `docker/whl` directory (ensure no additional whls are in the docker directory)

```
cp dist/k8s_vim_driver-<driver-version>-py3-none-any.whl docker/whls/
```

3. Navigate to the `docker` directory

```
cd docker
```

4. Build the docker image

```
docker build -t accanto/k8s-vim-driver:<driver-version> .
```

## Run Helm Chart

Run the helm chart, setting the Docker image version if different to the default in `helm/k8s-vim-driver/values.yaml`:

```
helm install helm/k8s-vim-driver --name k8s-vim-driver --set docker.version=<driver-version>
```

The above installation will expect Kafka to be running in the same Kubernetes namespace with name `foundation-kafka`, which is the default installed by Stratoss&trade; Lifecycle Manager. If different, override the Kafka address:

```
helm install helm/k8s-vim-driver --name k8s-vim-driver --set app.config.override.messaging.connection_address=myhost:myport
```

# Access Swagger UI

The Swagger UI can be found at `http://your_host:31680/api/infrastructure/ui` e.g. `http://localhost:31680/api/infrastructure/ui`
