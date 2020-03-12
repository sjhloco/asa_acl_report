# ASA ACL Report

ASA ACL Auditor v0.3 (tested 9.6)

Creates an XL sheet of the ACLs on an ASA with details of the hit counts and the last time the rule was hit.\
The row for rules that have been hit in the last day, 7 days and 30 days are colourised.\
Filters added to the XL header to aid drilling down further in larger rule bases.

The report can be run against an ASA or offline agaisnt a text file of the ASAs rule base. Either method can be filtered down to a subset of IP address and/or ACL names.

![image](https://user-images.githubusercontent.com/33333983/76520041-03b13200-645a-11ea-89f9-69203495963c.png)

To run offline you need to collect the following information and save it separate files in your home directory:

- **ACLs** *(mandatory)*: All the expanded access-lists (*show access-list*) you wish to evaluate against stored in the one single file.
- **ACL Brief** *(optional)*: To get the timestamp of the last hit you must have a second file with *show access-list <name> brief* for the ACLs. Any ACLs without this file will not have the timestamp information in the xl sheet.

## Prerequisites

The only extra packages required to run this are netmiko and openpyxl.

```bash
pip install -r requirements.txt
```

The first section of the script is the customisable default values. There is the option to change the default directory location (where to looks for offline files and saves the report), the report name, the device to run against and the XL header names (including column widths).

```bash
directory = expanduser("~")
device = 'ste@10.10.10.1'
eport_name = device.split('@')[1] + '_ACLreport_' + date.today().strftime('%Y%m%d')
header = {'ACL Name':22, 'Line Number':17, 'Access':10, 'Protocol':12, 'Source Address':19, 'Source Port':16, 'Destination Address':24,
          'Destination Port':20, 'Hit Count':14, 'Date Last Hit':17, 'Time Last Hit':17}
```

## Usage

When executed the script with no flags it will run against the default device, do no IP or ACL filtering and save the output to the file *~/device_ACLreport_yyyymmdd*. The following optional options (flags) can be used at runtime.

```bash
*-f or --filename:* Name of the files (ACL and optionally ACL Brief) to run the script against. If no file is specified it will run agaisnt a device (be that the default or specified one)
*-d or --device:* Username and device (*username@device*) to run the script against
*- or --ip:* IP addresses or networks (no prefix) to filter against (seperated by spaces)
*-a or --acl:* ACL names seperated by spaces to filter against
*-l or --location:* Location where the offline files are stored as well as the location to save the report
*-n or --name:* Name of the report
*-h, --help:* Information on these flags
```

### Run against ASA *(-d)*

When running against a device the IP adddress and username are entered in the cmd and the password prompted for. If the *-f flag (and filename)* is not used the script will always run against a device, be it the default or a specified one 

```bash
$python asa_v2.py -d ste@10.10.10.1

============================== ASA ACL Auditor v0.3 (tested 9.6) ==============================
Checking the options entered are valid...
Enter the ASA password:
```

### Run against File *(-f)*

When running against files users only need to specify the filename (including extensions) and the script will by default look in their home directory. The files will be sanitized by the script to remove any unneeded blank lines and commands as well as ensuring that it is not the output of *show run access-list*.

```bash
$python asa_v2.py -f acl.txt acl_brief.txt
```

### Filtering *(-i or -a)*

To gather a full list of all ACEs in all the ACLs their is no need to use the *-i* or *-a* flags. Alternatively, the report that is generated can be filtered down to specific addresses, ACLs, or a combination of both. All must be separated by a space and be either a valid address (no prefix or subnet mask supported) or a valid ACL name on the ASA or in the file (be careful with capitalization).

```bash
$python asa_v2.py -d ste@10.10.10.1 -a data mgmt -i 10.10.20.254 10.10.10.71 10.10.10.50

============================== ASA ACL Auditor v0.3 (tested 9.6) ==============================
Checking the options entered are valid...
Enter the ASA password:
Gathering ACL info from the ASA...
Formatting the ACL data...
Creating the spreadsheet...
File /Users/mucholoco/10.10.10.1_ACLreport_20200311.xlsx has been created
```

## Error Handling

If any of the ASA login details are incorrect you will get a descriptive error message and be prompted to re-enter.

NEED IMAGE

If the acl or acl_brief filename cannot located in the home directory you will be prompted to check and re-enter.

![image](https://user-images.githubusercontent.com/33333983/76521337-8e932c00-645c-11ea-9f71-0c6445b7d132.png)

If the destination filename entered already exists you will be prompted to ovewrite it or re-enter a new name.

![image](https://user-images.githubusercontent.com/33333983/76543551-9b287c00-647e-11ea-9098-2c93bdea69f6.png)

If the address entered is not in a valid IPv4 format or the ACL does not exist (on the ASA or in the ACL file) the script will fail with details of the offending item.

<img width="762" alt="image" src="https://user-images.githubusercontent.com/33333983/69009348-4e0f2000-094c-11ea-84df-5f0c452ea441.png">

<img width="836" alt="image" src="https://user-images.githubusercontent.com/33333983/69008486-06d06180-0943-11ea-87a5-d1361d325bc9.png">
