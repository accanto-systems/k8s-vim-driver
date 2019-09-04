# Vanilla Devstack

Use the [DevstackVagrant](http://git.lifecyclemanager.com/environments/devstackvagrant) project on Lifecyclemanager.com to install an all-in-one Openstack instance on a target VM.

## Installing on Simplivity 

When installing on Simplivity you must enable KVM passthrough by:
* Power off the VM
* Selecting your VM
* Select `Actions` from the VM menu
* Select `Edit Settings` from the dropdown menu
* Expand the `CPU` section of `Virtual Hardware`
* Enable the checkbox labelled `Expose hardware assisted virtualization to the guest OS`
* Power on the VM

You should then update the `public_interface` value in the `variables.yml` file to be `ens160` (check this is the public interface for your VM). The default settings for other variables should be fine. 

Also update the inventory file to reflect the IP and user information for your target VM.

# Openstack Client

Read [Openstack Client](Openstack_Client.md) to learn how to install and configure the Openstack command line client.
