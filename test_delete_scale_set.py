from lib.azure_connection import AzureConnection

def main():
    azure_conn = AzureConnection()
    
    vm_instance_id = azure_conn.get_random_scale_set_vm('scale-set2', 'scalesetf')
    if vm_instance_id is not None:
        azure_conn.delete_vm_from_scale_set('scale-set2', 'scalesetf', vm_instance_id)

if __name__ == '__main__':
    main()
