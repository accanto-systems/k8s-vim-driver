## Create

```
{
  "deploymentLocation": {
    "name": "default",
    "properties": {
      "k8s-server": "http://10.220.217.248:8080",
      "k8s-username": "admin"
    },
    "type": "k8s"
  },
  "inputs": {
    "name": "sg1",
    "image": "nginx:latest",
    "container_port": "80",
    "storage_size": "1",
    "storage_class": "microk8s-hostpath"
  },
  "template": "tosca_definitions_version: tosca_simple_yaml_1_0\ndescription: Basic example to deploy a single VM\nnode_types:\n  accanto.nodes.K8sCompute:\n    derived_from: tosca.nodes.Compute\n    properties:\n      image:\n        type: string\n      container_port:\n        type: integer\n  accanto.nodes.K8sStorage:\n    derived_from: tosca.nodes.BlockStorage\n    properties:\n      size:\n        type: integer\n      class:\n        type: string\ntopology_template:\n  inputs:\n    image:\n      type: string\n      default: nginx:alpine\n    container_port:\n      type: integer\n      default: 80\n    storage_size:\n      type: integer\n      default: 1\n    storage_class:\n      type: string\n      default: microk8s-hostpath\n  node_templates:\n    hello-world-server:\n      type: accanto.nodes.K8sCompute\n      capabilities:\n        host:\n          properties:\n            num_cpus: 2\n            disk_size: 10 GB\n            mem_size: 2 GB\n      properties:\n        image: { get_input: image }\n        container_port: { get_input: container_port }\n      requirements:\n        - local_storage:\n            capability: tosca.capabilities.Attachment\n            node: hello-world-storage\n            relationship:\n              type: tosca.relationships.AttachesTo\n              properties:\n                location: /data\n    hello-world-storage:\n      type: accanto.nodes.K8sStorage\n      properties:\n        size: { get_input: storage_size }\n        class: { get_input: storage_class }\n  outputs:\n    hello_world_private_ip:\n      description: The private IP address of the hello-world-server\n      value: { get_attribute: [hello-world-server, private_address] }"
}
```


{
  "deploymentLocation": {
    "name": "default",
    "properties": {
      "k8s-server": "http://10.220.217.248:8080",
      "k8s-username": "admin"
    },
    "type": "k8s"
  },
  "inputs": {
    "name": "sg1",
    "image": "nginx:latest",
    "container_port": "80",
    "storage_size": "1",
    "storage_class": "microk8s-hostpath"
  },
  "template": "tosca_definitions_version: tosca_simple_yaml_1_0\ndescription: Basic example to deploy a single VM\nnode_types:\n  accanto.nodes.K8sCompute:\n    derived_from: tosca.nodes.Compute\n    properties:\n      image:\n        type: string\n      container_port:\n        type: integer\n  accanto.nodes.K8sStorage:\n    derived_from: tosca.nodes.BlockStorage\n    properties:\n      size:\n        type: integer\n      class:\n        type: string\ntopology_template:\n  inputs:\n    image:\n      type: string\n      default: nginx:alpine\n    container_port:\n      type: integer\n      default: 80\n    storage_size:\n      type: integer\n      default: 1\n    storage_class:\n      type: string\n      default: microk8s-hostpath\n  node_templates:\n    hello-world-server:\n      type: accanto.nodes.K8sCompute\n      capabilities:\n        host:\n          properties:\n            num_cpus: 2\n            disk_size: 10 GB\n            mem_size: 2 GB\n      properties:\n        image: { get_input: image }\n        container_port: { get_input: container_port }\n      requirements:\n        - local_storage:\n            capability: tosca.capabilities.Attachment\n            node: hello-world-storage\n            relationship:\n              type: tosca.relationships.AttachesTo\n              properties:\n                location: /data\n    hello-world-storage:\n      type: accanto.nodes.K8sStorage\n      properties:\n        size: { get_input: storage_size }\n        class: { get_input: storage_class }\n  outputs:\n    hello_world_private_ip:\n      description: The private IP address of the hello-world-server\n      value: { get_attribute: [hello-world-server, private_address] }"
}



## Delete

```
{
  "deploymentLocation": {
"name": "default",
    "properties": {
      "k8s-server": "https://10.220.217.113:6443",
      "certificate-authority-data": "LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUN5RENDQWJDZ0F3SUJBZ0lCQURBTkJna3Foa2lHOXcwQkFRc0ZBREFWTVJNd0VRWURWUVFERXdwcmRXSmwKY201bGRHVnpNQjRYRFRFNU1EY3dNVEUyTVRnek5sb1hEVEk1TURZeU9ERTJNVGd6Tmxvd0ZURVRNQkVHQTFVRQpBeE1LYTNWaVpYSnVaWFJsY3pDQ0FTSXdEUVlKS29aSWh2Y05BUUVCQlFBRGdnRVBBRENDQVFvQ2dnRUJBUE82CjVYNHkvY1Erei9HRWorSVZ5Z1h0UU5iQVNFdm9uOTRJaUhKY25YTVlWdTVIcjdyVlFwd2VSczZWVEhoYlVGMVkKVmM5YWFzYUJFaXNreVVUOUExVHJtY3BRRzY5WjdVVGdEUGNCZ0E3dzhCTHRZMkN0QnJnUjkvWUphS3ZZV3hSUwo5Q2FDK2VEQWUyY0dCT3J1VkVnY1NUWmR2OU5jTmpnMGJqSzZlWTJjZEYrd25SaXQxeFBrSWxJZlBUSVg3elI1CmxMTWhNUjlLdnNuaVhML0tIUisxcnZsa2pxRHFLdFhkQ2dCazIzMmhhYmpoY2RWQ3k2MG92RjdYZlVldXpKaXgKRUxLTzhWUkx3Vm1NbFRJT2haOXRTRTZKTkR1L05sdVJTY1hOQ2FpQWdIbXhFcUdQYm42VlRudWxkRXFOSWVpNgp2LzhqajcrS1VnQk9RQ1lqV2VFQ0F3RUFBYU1qTUNFd0RnWURWUjBQQVFIL0JBUURBZ0trTUE4R0ExVWRFd0VCCi93UUZNQU1CQWY4d0RRWUpLb1pJaHZjTkFRRUxCUUFEZ2dFQkFGNFFmZER2blVnbEZ2TDdmM2ZPMTRNRG1OVUwKTXB5di9PTE1IR2hyNm01MTdxaU11cXBVNGdDcERpVVFaOGZJTVpHQklwbHJvd0Q4ejJKRWsraHhwc2ZMSkUzUgp5NTlST2F0ZkV5SURtTTMwQ2dBb1pkb2liemJTdVpZZ2tjaENpRnNTMmlDSUY1UXlFa3F5NFlpRWNKSDZDWUZVCjZNOE9hMXBYcDNqTTdmYUx5MXRDRy9YYkFQREFRQ0hmVjdXWWlMZkEvaHJaNWkvajV4WnEyMno0U0k2TFBPZE0Kd1ExbFp6emZOVWVDeEd4UXp4bjJzazMzdXVDVXo4ZjJBOHdKSFBpZlprNCtycGxCOXIydExvNzJPU2ErazVrdAo3NWROMnBDd1dBSG5jU2JYRDFwQWw0M0s5OVdCeE9qN3hRZUMrZjRBaEYrWEZUYkFrUWlQY3F3bkRXVT0KLS0tLS1FTkQgQ0VSVElGSUNBVEUtLS0tLQo=",
      "client-certificate-data": "LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUM4akNDQWRxZ0F3SUJBZ0lJY0kvNXY2a0hZQkV3RFFZSktvWklodmNOQVFFTEJRQXdGVEVUTUJFR0ExVUUKQXhNS2EzVmlaWEp1WlhSbGN6QWVGdzB4T1RBM01ERXhOakU0TXpaYUZ3MHlNREEyTXpBeE5qRTRORFJhTURReApGekFWQmdOVkJBb1REbk41YzNSbGJUcHRZWE4wWlhKek1Sa3dGd1lEVlFRREV4QnJkV0psY201bGRHVnpMV0ZrCmJXbHVNSUlCSWpBTkJna3Foa2lHOXcwQkFRRUZBQU9DQVE4QU1JSUJDZ0tDQVFFQTNIbmgrOVhnMCtaMUE3SXoKQ3VLNTdHdzNQemRaTWEvaWMwY0pTY1pLRzFUZ1kzWnk2aEh0Vm9uRkdlb0VNQkNGak5NTllHRTNNYUIrd0VMWQp0RnIzMVk1bVAwcm01R2dMM2pvSklkaUl5amhCaVBxSDVxT3V3MzFMcTFKTDhLclVKSEV2VlpLK3dZaEY2amlaCm1TSEZHQkNFVndOb25JMVEzdzhyYU5WZEtWRUZUb3k2ZHIvMVAvMjlSaERDdXBjU0hubmN3MWZhbDFtL0VhUnAKNnorYzlVdnFZQ1FJdWl6NzAwRWFEQkVRcWw1bkNrclNHMzFkbmZkYjNNVDlYSWFFNzNsaFJhUmpjdmJDQ04xdgpyNFRCejlZV3YxcnRMYjUvNFIvUW9Cd1R0VW5WM0F0TkwyZkt3MTlxQTNsTjFtSnk5YlpsNzNId25qRmpmbmxnCmNyVWpHUUlEQVFBQm95Y3dKVEFPQmdOVkhROEJBZjhFQkFNQ0JhQXdFd1lEVlIwbEJBd3dDZ1lJS3dZQkJRVUgKQXdJd0RRWUpLb1pJaHZjTkFRRUxCUUFEZ2dFQkFMYlViNEtaZ2VVOEVVTXJSK3dqSmZnNFFCUVU3bEU5WkdXYwp2NENDcFVaMERHV3d0ZzRWUmpPZmRhNXkxSjdjYk9uVW9pbjVFcEtRcWtJMmxLbGZMdzgzMUxsTnYrSHo0U1N3CmZmQ0VHUEQyTkc3OWxzclRRNjZxNXJXcVpaaXNSVHhwZ212OEoyTHovY3h3eU5GSGdVSTBUVXM1cGdrTlR3WGIKWEJPeE5FMS9uVTFoaTFKM1ZJN2VNRVkrWjZEbjRiUWVTelZGL3ZKLzJPL2hCM2xGenRRSmV0QVJZcUR2dlNNaQprTTdqa2tzQWFNcXVkOHhRU3BScFJiT01paUdoSmx6VUFkSzA3NjQvNDRTREtuVHhJN3hWQ2UrOUVCR2psRGE2CkplQTV4MEZkZkJxWnBKZml3M3lJMDhtaHpGZFhlWllGL3Q2S3FSZlV1ZVI3VXFUSUFsRT0KLS0tLS1FTkQgQ0VSVElGSUNBVEUtLS0tLQo=",
      "client-key-data": "LS0tLS1CRUdJTiBSU0EgUFJJVkFURSBLRVktLS0tLQpNSUlFcFFJQkFBS0NBUUVBM0huaCs5WGcwK1oxQTdJekN1SzU3R3czUHpkWk1hL2ljMGNKU2NaS0cxVGdZM1p5CjZoSHRWb25GR2VvRU1CQ0ZqTk1OWUdFM01hQit3RUxZdEZyMzFZNW1QMHJtNUdnTDNqb0pJZGlJeWpoQmlQcUgKNXFPdXczMUxxMUpMOEtyVUpIRXZWWksrd1loRjZqaVptU0hGR0JDRVZ3Tm9uSTFRM3c4cmFOVmRLVkVGVG95Ngpkci8xUC8yOVJoREN1cGNTSG5uY3cxZmFsMW0vRWFScDZ6K2M5VXZxWUNRSXVpejcwMEVhREJFUXFsNW5Da3JTCkczMWRuZmRiM01UOVhJYUU3M2xoUmFSamN2YkNDTjF2cjRUQno5WVd2MXJ0TGI1LzRSL1FvQndUdFVuVjNBdE4KTDJmS3cxOXFBM2xOMW1KeTliWmw3M0h3bmpGamZubGdjclVqR1FJREFRQUJBb0lCQVFDMlZ4TC96VVlRMmdNaQptR2xBY255anZHZ0FuMHprRy91anJUZFFUVzhTcGFLaWY5N1FHUjE1dVoxS0xsRmlVdmV3blFmdUV0aXI4WG1DCmxvWlV1dnRISW1zTG8yM0xyd1ZKdUNPL1d5N2VWNkpUb0Nkdkp5WXRSVjJraGY2S1B5NE9LWkdsS3lVYU9CTGkKZ0FjQUwzNnF4VlkrQkhLckx2Q1lXaHBqckRwTkpNdTV2OUhKa3BIV3ZBbzFEcm5SY2kwbnR4THB5L3pQcVN4NApOcmc4NXg3YlVVQ1MvbXNNNUJRQWVKcTV6NnZ4WFQ3MTZiTmZJUEJRaEE0L2ZPTUZXYkRPbnVheGgySW80N3lxClMxMGVkeEpPemc0SE5RSURiK2w1YU1YckFJeUc5U3BkM1RVaWd0OXAyRTFLYnVoWmxCMkJJS0ZNaDZTOGdIckoKa3h0dGtxMEZBb0dCQU55T200OElCMW90U2FTTGYyeDAyLzZoWUNPYW82eTdPSkx5WStoQ0I5dXRlalI0VGl1bApUa2lzZWJnckdYN3k0UGprZ2VaVlNOSWJkSWprOVhaeHJhdWg1TnlsbEprMmpUeFF2R1BSVHJsV0cwODhzSGJPCnQ1Qy9STTVidGxmNnQ4cG9mdjBKdUZBUE1Fbm8zVVpNRDc3K2dkZjhSWE9tQXIzVDNoL3BVbHZMQW9HQkFQL24KOGRWRlVQTUg4ZGp6bE5CWGRpY20xZW9rdktGM01ocXhHUGkwajZaQXAxU0Z0MjFtcERITTZJMWFmeSs4RU5rVwpzUFJQVHNRTzNOcDJDb3VUK0hxbVFrUjVKdVIyWUJQLzVJUmhXQTlRc3FNc2hSMkZrRTdCZmc5c0YrWGFMZWhRCnpVUVhIb1ExU3dLakxJdUZvcTlCYVFSd1pqSEpGMTY2b2ZSSm1DZ3JBb0dBRU9KVjVFQXdGK1lwb2hBUHhDUzYKQnFjaDdmZlRtZENIUnpDSkYybWVvbUdJWG1YclRnb01rU0dxKzc5STUxLytldTg3Um4rMjRHYTdxQk1tKzFjKwpmVW9hZEEyMDczbXVuRFJ1QjVJcFhhVEsyR2tEOVVSajV3L05XNkxIdGJwNndXTDRmYlIxeUtNeEJpZHVjUWczCm1GNXhZREJ1dktpend3WnFGYlZOMmJzQ2dZRUF2VXgzVUxzQXdYWk1DWjlOb3J3Lzg0QS8xdjhyNWdrRk1FZDIKNEdxNHBGUEpNN1hpVlBRTFc2ZG5FMEV4T2o5VSt6RlUzclJYNEtIWjcyUklNcTNYcmVxVXRKQW1HL1FRNkZwdgpVUm10Q1U4NWhZam1RMHRNejJWRWVlWU0yNE9FV0FpRmZ1dlhNQmM0RUpCaDRDZVBpekxJbTNjRnNhZytPRjI0CmRidUc2WmNDZ1lFQXVyazVwTlZpR1dPVG05NEt0NllMa3cwdGxPLzR1YkM0dHBPYzJINTNtaFgrNHpGN2dxNzYKQVJ2emxvYjBGQms2SkFvRjBnNG1IUTF5cVNVOHY2eWpNUGp6TnhjaVpFME1RclFkbWJ1QXBFNkZBb3BZRUlObgpRdExkQitvdE5jeEM1MXhxUHBlRGZ5VFUwWFBMN1pyaEFqU2t6QUFSeVF3U3V3c01VRFBlTnFBPQotLS0tLUVORCBSU0EgUFJJVkFURSBLRVktLS0tLQo="
    },
    "type": "k8s"
  },
  "infrastructureId": "6ba4b038a22d487894b0da4ac0896fd7",
  "requestId": "6ba4b038a22d487894b0da4ac0896fd7"
}
```