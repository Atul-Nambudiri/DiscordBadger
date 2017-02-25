from lib.azure_connection import AzureConnection

def main():
    azure_conn = AzureConnection()
    
    vm_name = azure_conn.get_random_resource_group_vm('test1')
    associated_info = azure_conn.get_resource_group_vm_associated_network_info('test1', vm_name)
    azure_conn.delete_vm_from_resource_group('test1', vm_name)
    for interface in associated_info:
        azure_conn.delete_nic_from_resource_group('test1', interface['interface_name'])
        if 'network_security_group' in interface:
            azure_conn.delete_nsg_from_resource_group('test1', interface['network_security_group'])
        if 'ips' in interface:
            for ip in interface['ips']:
                azure_conn.delete_ip_from_resource_group('test1', ip)


if __name__ == '__main__':
    main()