from lib.azure_connection import AzureConnection

def main():
    azure_conn = AzureConnection()

    vm_name = azure_conn.get_random_resource_group_vm('vm-set')
    if vm_name is not None:
        azure_conn.delete_vm_from_resource_group('vm-set', vm_name)

if __name__ == '__main__':
    main()
