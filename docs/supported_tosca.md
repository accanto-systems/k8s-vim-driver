# Tosca Types

Below is the full definition of the extended TOSCA types included in this driver:

```
tosca_definitions_version: tosca_simple_yaml_1_0

description: Custom types supported out-of-the-box by this driver

node_types:
  tosca_definitions_version: tosca_simple_yaml_1_0
description: Test
node_types:
  ##########################
  ## Custom K8s Types
  ############################

  ## The following types are K8s specific

  accanto.nodes.K8sNetwork:
    derived_from: tosca.nodes.Root
    description: a Kubernetes network other than the main network (realised using a CNU plugin such as [Multus](https://github.com/intel/multus-cni))
    properties:
      name:
        type: string
        description: the name of the K8s network (must already exist)
        required: true
    attributes:
      address:
        type: string
        required: false
        description: the IP address of the Compute Pod network once it has been attached to the Compute Pod

    accanto.nodes.K8sCompute:
        derived_from: tosca.nodes.Compute
        description: creates a Kubernetes pod
        properties:
            image:
                type: string
                description: The Docker image name:tag
                required: true
            container_port:
                type: integer
                description: The port on which the resource listens (if any)
                required: false

    accanto.nodes.K8sStorage:
        derived_from: tosca.nodes.BlockStorage
        description: creates a Persistent Volume Claim (PVC) for a compute pod
        properties:
            size:
                type: integer
                description: the size of the storage (currently sets persistent volume claim resource requests for the compute pod) e.g. 8Gi
                required: true
            class:
                type: string
                description: the K8s storage class (must exist in the K8s cluster)
                required: true
```
