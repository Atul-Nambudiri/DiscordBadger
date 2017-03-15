# ChaosMonkey for Azure (DiscordBadger)

# Description
[ChaosMonkey](https://github.com/Netflix/chaosmonkey) is a system developed in house at Netflix to test the resiliency and fault-tolerance of various services on their AWS stack. 

The goal of this project is to produce a similar system on Microsoft Azure, so that developers can do similar resiliency testing.

DiscordBadger automatically restarts or deletes VMs in Azure Resource Groups, Scale Sets, and Container Services. This can be used to test how systems react to unexpected failures.

# Requirements:
SQLite must be installed.

The following Python modules are also required. They can be installed via pip:
1. azurerm ( pip install azurerm )
2. azure ( pip install --pre azure )

# Setup:
You will need to create an Active Directory application and service principal, and give them access to your Azure subscription. Instructions can be found [here](http://azure-sdk-for-python.readthedocs.io/en/latest/quickstart_authentication.html?highlight=ServicePrincipalCredentials)

You will need to provide DiscordBadger the subscription id, client id, secret, and tenant id.
These are read in from the following environment variables:

1. subscription_id -> AZURE_SUBSCRIPTION_ID
2. client_id -> AZURE_CLIENT_ID
3. secret -> AZURE_CLIENT_SECRET
4. tenant -> AZURE_TENANT_ID

Once you set these variables, DiscordBadger should be able to access your Azure project.

You also need to setup the SQLite database to hold all schedule information. To do this, create a SQLite database in the project folder. Then, execute the commands within db_init.txt
After that, set the database_file_name parameter within common_config.json to be the name of the database file.

# Usage
DiscordBadger works on individual resource groups. Its allows you to define schedules, which are particular resource types of delete vms on. Resource Groups, Scale Sets, and Container Services are the three supported types.

You add schedules by running add_schedule.py, and you run a schedule using run_schedule.py. There are certain parameters that you must define when you create a schedule. They are the following:

 * Schedule Name: The name that you are defining for a schedule.
 * Resource Type: This is which one of the three resource types the particular schedule should work on. This is required
 * Resource Group: The resource group that the VMS/Scale-Set/ContainerService is contained within. This is required
 * Action: Whether you want to restart or delete the VM. This is required
 * Run Probability: This is the probability that the VM will be restarted/deleted. Every time you run run_schedule.py, this is the probability that an action will be taken on the resource type. This defaults to .5. You can change the default in common_config.json.
 * Scale Set: If you are defining a scale set, you have to choose which scale set in the resource group you want to take action on. You also have to define one for Container Services.

 You can pass these in as command line parameters, or you cna define them in a JSON file that you pass in. There is a sample JSON file you can follow in sample_schedule.json

 You can run a schedule by executing run_schedule.py. It accepts on optional parameter:
 Schedule-name: This is the name of the schedule you want to run. If you don’t provide a name, it defaults to running all the defined schedules.

 When running a schedule, DiscordBadger looks at the resource group you have chosen for the schedule. For both Resource Groups, and Scale Sets, the system looks the resource and chooses a random vm within it. If no VM exists, the system returns. Otherwise, it looks at the run_probability that has been defined for the schedule. It has that probability of running the schedule, and deleting or restarting the vm that was chosen.

 While running a schedule on a Container Service, it uses the run_probability to choose whether the system runs on the Scale Set that is defined for a Container Service, or on the individual vm’s that are defined for them.
