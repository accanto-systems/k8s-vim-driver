# Build

docker build --build-arg DRIVER_VERSION=0.0.1a0 --build-arg PYPI_REPO_IP=10.220.217.248 --build-arg PYPI_REPO_URI=http://10.220.217.248:32739/repository/pypi-all/simple -t k8s-vim-driver:0.1.0dev0 .

