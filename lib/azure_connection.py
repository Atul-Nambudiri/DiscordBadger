import os
import re
import random

import azurerm

from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.common.credentials import ServicePrincipalCredentials

class AzureConnection():
    def __init__(self, subscription_id = os.environ['AZURE_SUBSCRIPTION_ID'],
                       client_id = os.environ['AZURE_CLIENT_ID'],
                       secret = os.environ['AZURE_CLIENT_SECRET'],
                       tenant = os.environ['AZURE_TENANT_ID']):
      self.subscription_id = subscription_id
      self.azure_client_credentials = ServicePrincipalCredentials(
            client_id = client_id,
            secret = secret,
            tenant = tenant)

      self.compute_client = ComputeManagementClient(self.azure_client_credentials, subscription_id)
      self.network_client = NetworkManagementClient(self.azure_client_credentials, subscription_id)
      
      self.azurerm_credentials = azurerm.get_access_token(
            tenant, 
            client_id, 
            secret)

    def get_compute_client(self):
      return self.compute_client

    def get_network_client(self):
      return self.network_client




    def get_resource_group_ips(self, resource_group):
      return azurerm.list_public_ips(self.azurerm_credentials, self.subscription_id, resource_group)['value']

    def get_random_resource_group_ip(self, resource_group):
      ips = self.get_resource_group_ips(resource_group)
      if len(ips) == 0:
        return None
      return ips[random.randint(0, len(ips) -1)]['name']

    def delete_ip_from_resource_group(self, resource_group, ip_name):
      print("Deleting IP Address %s from Resource Group %s" % (ip_name, resource_group))
      return self.network_client.public_ip_addresses.delete(resource_group, ip_name).wait()




    def get_resource_group_nics(self, resource_group):
      return azurerm.list_nics_rg(self.azurerm_credentials, self.subscription_id, resource_group)['value']

    def get_random_resource_group_nic(self, resource_group):
      nics = self.get_resource_group_nics(resource_group)
      if len(nics) == 0:
        return None
      return nics[random.randint(0, len(nics) -1)]['name']

    def delete_nic_from_resource_group(self, resource_group, nic_name):
      print("Deleting NIC %s from Resource Group %s" % (nic_name, resource_group))
      return self.network_client.network_interfaces.delete(resource_group, nic_name).wait()

    def get_nic_info(self, resource_group, nic_name):
      return azurerm.get_nic(self.azurerm_credentials, self.subscription_id, resource_group, nic_name)




    def delete_nsg_from_resource_group(self, resource_group, nsg_name):
      print("Deleting NSG %s from Resource Group %s" % (nsg_name, resource_group))
      return self.network_client.network_security_groups.delete(resource_group, nsg_name).wait() 




    def get_resource_group_vms(self, resource_group):
      return azurerm.list_vms(self.azurerm_credentials, self.subscription_id, resource_group)['value']

    def get_resource_group_vm_info(self, resource_group, vmName):
      return azurerm.get_vm(self.azurerm_credentials, self.subscription_id, resource_group, vmName)

    def get_random_resource_group_vm(self, resource_group):
      vms = self.get_resource_group_vms(resource_group)
      if len(vms) == 0:
        return None
      return vms[random.randint(0, len(vms) -1)]['properties']['osProfile']['computerName']

    def delete_vm_from_resource_group(self, resource_group, vm_name):
      print("Deleting VM %s from Resource Group %s" % (vm_name, resource_group))
      return self.compute_client.virtual_machines.delete(resource_group, vm_name).wait()

    def restart_vm_in_resource_group(self, resource_group, vm_name):
      print("Restarting VM %s in Resource Group %s" % (vm_name, resource_group))
      return self.compute_client.virtual_machines.restart(resource_group, vm_name).wait()

    


    def get_scale_set_info(self, resource_group, scale_set_name):
      return azurerm.get_vmss(self.azurerm_credentials, self.subscription_id, resource_group, scale_set_name)

    def get_scale_set_vms(self, resource_group, scale_set_name):
      return azurerm.list_vmss_vms(self.azurerm_credentials, self.subscription_id, resource_group, scale_set_name)['value']

    def get_random_scale_set_vm(self, resource_group, scale_set_name):
      vms = self.get_scale_set_vms(resource_group, scale_set_name)
      if len(vms) == 0:
        return None
      return vms[random.randint(0, len(vms) - 1)]['instanceId']

    def delete_vm_from_scale_set(self, resource_group, scale_set_name, instance_id):
      print("Deleting VM %d in Scale-Set %s from Resource Group %s" % (instance_id, scale_set_name, resource_group))
      return self.compute_client.virtual_machine_scale_sets.delete_instances(resource_group, scale_set_name, [instance_id]).wait()

    def restart_vm_in_scale_set(self, resource_group, scale_set_name, instance_id):
      print("Restarting VM %d in Scale-Set %s in Resource Group %s" % (instance_id, scale_set_name, resource_group))
      return self.compute_client.virtual_machine_scale_sets.restart(resource_group, scale_set_name, [instance_id]).wait()




    def get_resource_group_vm_associated_network_info(self, resource_group, vmName):
      return_info = []
      pattern = '\/.*\/(.*)'

      vm_info = self.get_resource_group_vm_info(resource_group, vmName)
      network_interfaces = vm_info['properties']['networkProfile']['networkInterfaces']
      for interface in network_interfaces:
          info = {}
          match = re.search(pattern, interface['id'])
          interface_name = match.group(1)
          info['interface_name'] = interface_name

          nic_info = self.get_nic_info(resource_group, interface_name)['properties']

          if 'networkSecurityGroup' in nic_info:
            network_security_group = nic_info['networkSecurityGroup']['id']
            match = re.search(pattern, network_security_group)
            network_security_group_name = match.group(1)
            info['network_security_group'] = network_security_group_name

          if 'ipConfigurations' in nic_info:
            ip_configurations = nic_info['ipConfigurations']
            ips = []
            for config in ip_configurations:
                ip = config['properties']['publicIPAddress']['id']
                match = re.search(pattern, ip)
                ip_name = match.group(1)
                ips.append(ip_name)
            info['ips'] = ips
          return_info.append(info)
      return return_info
