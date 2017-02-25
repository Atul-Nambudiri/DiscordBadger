from lib.azure_connection import AzureConnection

def main():
    azure_conn = AzureConnection()

    ip_name = azure_conn.get_random_resource_group_ip('test')
    if ip_name is not None:
        azure_conn.delete_ip_from_resource_group('test', ip_name)

if __name__ == '__main__':
    main()