# ASA ACL Report

ASA ACL Auditer v0.2 (tested 9.6)

This tool will create a CSV file of the ACLs on an ASA with details of the hit counts and the last time the rule was hit. The results can be filtered down to a specific subset of ACLs and addresses.

IMAGE

The report can either be generated from the ASA or offline and run against previously extracted command outputs.
To run offline you need to collect the following information and save in separate files in your home directory:
**-ACLs** *(mandatory)*: All the expanded access-lists (*show access-list*) you wish to evaluate against stored in the 1 single file.
**-ACL Brief** *(optional)*: To get the timestamp of the last hit must have a second file with *show access-list <name> brief* for the ACLs. Any ACLs without this file you will not get the timestamp information in the csv.

## Prerequisites

The only extra package required to run this is netmiko, this is used for the SSH connections to the device. To install
'''
pip install -r requirements.txt
'''

The first section of the script is the Variables section. In here you can change the default directory location (where it saves the CSV and looks for offline files) and customize the CSV header names.
'''json
directory = expanduser("~")
csv_columns = ['ACL Name', 'Line Number', 'Access', 'Protocol', 'Source Address', 'Source Port',
               'Destination Address', 'Destination Port', 'Hit Count', 'Date Last Hit', 'Time Last Hit']
'''

## Usage

The information gathered in the script is all done from user interaction once the script has been run. To get started enter:
'''
python asa_acl_report.py
'''

IMAGE

- When running against a device the IP adddress, username and password are required.

IMAGE

If any of these are entered incorrectly will gte a descriptive error message and be promterd to enter again.

TWO IMAGES

- When running against files you need to specify the full filename (including extensions). The files will be santarised to remove any unneeded blank lines and cmds as well as ensuring that it is not the output of *show run access-list*

IMAGE
If the filename is not located in the hoem directory will be prompted to check and enter again.

IMAGE

If you only want the full list of all ACEs in all ACLs you can leave the the next two options blank and just enter the file name for the results.

IMAGE

If the file name entered already exists you will be prompted to ovewrite it or re-enter a new name.

IMAGE

## Filtering

The report that is generated can be filtered down to specific IP/ network addresses, ACLs, or a combination of both. All must be separated by a space, and be either a valid address (no prefix or subnet mask supported) or a valid ACL name on the ASA (be careful with capitalization).

IMAGE

If the address entered is not in a valid IPv4 format or the ACL does not exist (on the ASA or in the ACL file) the script will fail with details of the offending item.

IMAGE