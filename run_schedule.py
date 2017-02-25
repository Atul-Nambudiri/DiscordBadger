import random
import argparse

from lib.schedule_manager import ScheduleManager
from lib.azure_connection import AzureConnection
from lib.json_parse import parse_json

file_json = parse_json("common_config.json")
valid_resource_types = file_json["valid_resource_types"]
database_name = file_json['database_file_name']

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--schedule-name", help="The name of the schedule")
    args = parser.parse_args()

    schedule_manager = ScheduleManager(database_name)
    schedule_n = args.schedule_name
    
    schedules = {}

    if schedule_n is None:
        print("Running all schedules")
        schedule_list = schedule_manager.get_all_schedules()
        for schedule in schedule_list:
            schedules[schedule[0]] = schedule
    else:
        schedule = schedule_manager.get_schedule(schedule_n)
        if not schedule:
            print("A schedule with that name does not exist")
            return
        schedules[schedule_n] = schedule

    for schedule_name, schedule in schedules.iteritems():
        if schedule[1] not in valid_resource_types:
            print("The resource type for this schedule is %s, which is not valid" % (schedule[1]))
        else:
            print("Running Schedule " + schedule_name)
            azure_conn = AzureConnection()
            compute_client = azure_conn.get_compute_client()
            run_delete_probability = random.random()
            if run_delete_probability <= schedule[3]:
                print("Using Action %s for Schedule %s" % (schedule[5], schedule_name))
                schedule_type = schedule[1]
                if schedule_type == 'container-service':    
                    scale_set_functionality = random.random()   #If the types is a container service, you either work on a vm in the vm scale set, or one of the master vms, with the normal vm functionality
                    if scale_set_functionality <= schedule[3]:
                        schedule_type = 'scale-set'
                    else:
                        schedule_type = 'vm'
                if schedule_type == 'scale-set':
                    vm_instance_id = azure_conn.get_random_scale_set_vm(schedule[2], schedule[4])
                    if vm_instance_id is not None:
                        print("Acting on VM %d in Scale Set %s" % (vm_instance_id, schedule[4]))
                        if schedule[5] == "destroy":         #Check what the action is 
                            azure_conn.delete_vm_from_scale_set(schedule[2], schedule[4], vm_instance_id)
                        else:
                            azure_conn.restart_vm_in_scale_set(schedule[2], schedule[4], vm_instance_id)
                    else:
                        print("No VMS in Scale Set %s in Resource Group %s" % (schedule[4], schedule[2]))
                elif schedule_type == 'vm':
                    vm_name = azure_conn.get_random_resource_group_vm(schedule[2])
                    if vm_name is not None:
                        print("Acting on VM %s" % (vm_name))
                        associated_info = azure_conn.get_resource_group_vm_associated_network_info(schedule[2], vm_name)
                        if schedule[5] == "destroy":         #Check what the action is  
                            azure_conn.delete_vm_from_resource_group(schedule[2], vm_name)
                            for interface in associated_info:
                                azure_conn.delete_nic_from_resource_group(schedule[2], interface['interface_name'])
                                if 'network_security_group' in interface:
                                    azure_conn.delete_nsg_from_resource_group(schedule[2], interface['network_security_group'])
                                if 'ips' in interface:
                                    for ip in interface['ips']:
                                        azure_conn.delete_ip_from_resource_group(schedule[2], ip)
                        else:
                            azure_conn.restart_vm_in_resource_group(schedule[2], vm_name)
                    else:
                        print("No VMS in Resource Group " + schedule[2])


if __name__ == "__main__":
    main()