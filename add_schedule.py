import argparse

from lib.schedule_manager import ScheduleManager
from lib.json_parse import parse_json

file_json = parse_json("common_config.json")
valid_resource_types = file_json["valid_resource_types"]
valid_actions = file_json['valid_actions']
database_name = file_json['database_file_name']

def main():
    parser = argparse.ArgumentParser()
    required = parser.add_argument_group('You need to either pass in these required arguments, or pass in a schedule json file with the --file argument. There is a sample at sample_schedule.json')
    required.add_argument("--schedule-name", help="The name of the schedule")
    required.add_argument("--resource-type", help="The type of resource to modify. Right now these types are supported: %s" % (", ".join(valid_resource_types)))
    required.add_argument("--resource-group", help="The name of the resource group")
    required.add_argument("--action", help="The action to take on the specified resource_group. Right now, these actions are supported: %s" % (", ".join(valid_actions)))
    parser.add_argument("--file", help="You can set arguments in a file instead of passing in through the command line")
    parser.add_argument("--run-probability", help="A float between 0 and 1. This represents the probability that a scedule will be run. Defaults to .5")
    parser.add_argument("--scale-set-name", help="The name of a scale-set in a resource group to target")
    args = parser.parse_args()

    schedule_name = args.schedule_name
    resource_type = args.resource_type
    resource_group = args.resource_group
    run_probability = args.run_probability
    scale_set_name = args.scale_set_name
    action = args.action
    file = args.file

    if file != None:
        try:
            res = parse_json(file)
            schedule_name = res['schedule_name'] if res['schedule_name'] is not "" else None
            resource_type = res['resource_type'] if res['resource_type'] is not "" else None
            resource_group = res['resource_group'] if res['resource_group'] is not "" else None
            run_probability = res['run_probability'] if res['run_probability'] is not "" else None
            scale_set_name = res['scale_set_name'] if res['scale_set_name'] is not "" else None
            action = res['action'] if res['action'] is not "" else None
        except (IOError, OSError) as e:
            print("Could not open the passed in file")
            return
        except KeyError as e:
            print("Your JSON file does not have the correct keys")
            return
        except ValueError as e:
            print("Your JSON file is not formatted correctly")
            return

    # Verify that the required parameters are present
    if schedule_name is None or resource_type is None or resource_group is None or action is None:
        print("The Schedule Name, Resource Type, Resource Group, and Action can't be none")
        return

    # Verfiy that the resource_type is valid
    if resource_type not in valid_resource_types:
        print("The passed in resource_type is not valid. Right now these types are supported: %s" % (", ".join(valid_resource_types)))
        return

    #Verify that the action is valid
    if action not in valid_actions:
        print("The passed in action is not valid. Right now, these actions are supported: %s" % (", ".join(valid_actions)))
        return

    if run_probability == None:
        run_probability = .5

    # Verify that the run_probability is float
    try:
        run_probability = float(run_probability)
    except ValueError:
        print("Run probability is not a float")
        return

    schedule_manager = ScheduleManager(database_name)
    exists = schedule_manager.get_schedule(schedule_name)
    if exists:
        print("A schedule with that name already exists")
        return
    schedule_manager.create_schedule(schedule_name, resource_type, resource_group, action, run_probability, scale_set_name)


if __name__ == "__main__":
    main()