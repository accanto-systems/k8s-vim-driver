# Openstack Client

## Python Client

Install the [Openstack Python Client](https://github.com/openstack/python-openstackclient):

```
pip3 install python-openstackclient
```

Check the client is installed:

```
openstack --version
```

View the full set of commands offered by the client:

```
openstack --help
```

The client requires connection details for your instance of Openstack. Configure the client by exporting the following environment variables:

```
export OS_AUTH_URL=http://YOUR_HOST_IP/identity/v3/
export OS_PROJECT_NAME=YOUR_PROJECT_NAME
export OS_PROJECT_DOMAIN_NAME=default
export OS_USER_DOMAIN_NAME=default
export OS_IDENTITY_API_VERSION=3
export OS_PASSWORD=YOUR_PASSWORD
export OS_USERNAME=YOUR_USER_NAME
```

It's recommended to create a `sh` file with the above contents so you can perform the following command to configure your connection:

```
. /path/to/your/file

e.g.
. admin-openrc.sh
```

Once configured you are set to use the client.