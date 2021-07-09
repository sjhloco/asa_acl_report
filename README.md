[![published](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg)](https://developer.cisco.com/codeexchange/github/repo/sjhloco/asa_acl_report)

# ASA ACL Report

ASA ACL Auditor v0.3 (tested 9.8)

Creates an XL sheet of the ACLs on an ASA with details of the hit counts and the last time the rule was hit.\
The rows for rules that have been hit in the last day, 7 days and 30 days as well as inactive ACEs are colourised.\
Filters have been added to the worksheet header to aid drilling down further in larger rule bases.

The report can be run against an ASA or offline against a text file of the ASAs rule base. Either method can be filtered down to a subset of IP address and/or ACL names.

![image](https://user-images.githubusercontent.com/33333983/77829152-1f822c80-7118-11ea-83e8-1a431015f488.png)

To run offline you need to collect the following information and save it to separate files in your home directory:

- **ACLs** *(mandatory)*: All the expanded access-lists (*show access-list*) to report against stored in the one single file.
- **ACL Brief** *(optional)*: *show access-list acl_name brief* for all the the ACLs in the first file. Any ACLs without this file will not have the timestamp information of the last hit in the XL worksheet.

## Installation and Prerequisites

Clone the repository and create a virtual environment (in example is in a directory in home directory called *venv*):

```bash
git clone https://github.com/sjhloco/asa_acl_report.git
python -m venv ~/venv/asa_acl_report
source ~/venv/asa_acl_report/bin/activate
```

Now can install the packages required to run this script. The only extra packages required to run this are netmiko, openpyxl and pytest (optional for unit testing).

```bash
pip install -r asa_acl_report/requirements.txt
```

The first section of the script is the customisable default values. There is the option to change the default directory location (where to looks for offline files and saves the report), the report name, the device to run against and the XL header names (including column widths).

```bash
directory = expanduser("~")
device = 'ste@10.10.10.1'
report_name = device.split('@')[1] + '_ACLreport_' + date.today().strftime('%Y%m%d')
header = {'ACL Name':22, 'Line Number':17, 'Access':10, 'Protocol':12, 'Source Address':19, 'Source Port':16, 'Destination Address':24, 'Destination Port':20, 'Hit Count':14, 'Date Last Hit':17, 'Time Last Hit':17, 'State':10}
```

## Usage

When executed the script with no flags it will run against the default device, do no IP or ACL filtering and save the output to the file *~/device_ACLreport_yyyymmdd*. The following optional flags can be used at runtime.

```bash
-f or --filename: Name of the files (ACL and optionally ACL Brief) to run the script against. If no file is specified it will run against a device (be that the default or specified one)
-d or --device: Username and device (username@device) to run the script against
-i or --ip: IP addresses or networks (no prefix) to filter against (separated by spaces)
-a or --acl: ACL names separated by spaces to filter against
-l or --location: Location where the offline files are stored as well as the location to save the report
-n or --name: Name of the report
-h or --help: Information on these flags
```

### Run against ASA

When running against a device the IP address and username are entered in the cmd and the password prompted for. If the *-f flag (and filename)* is not used the script will always run against a device, be it the default or a specified one.

```bash
$python asa_acl_report_v3.py -d ste@10.10.10.1

========================== ASA ACL Auditor v0.3 (tested 9.8) ==========================
Checking the options entered are valid...
Enter the ASA password:
```

### Run against File

When running against files users only need to specify the filename (including extensions) and the script will by default look in their home directory. The files will be sanitized by the script to remove any unneeded blank lines and commands as well as ensuring that it is not the output of *show run access-list*. Only the output of *show run access-list* is mandatory, *show access-list acl_name brief* is optional.

```bash
$python asa_acl_report_v3.py -f acl.txt acl_brief.txt
```

### Filtering the input

To gather a full list of all ACEs in all the ACLs their is no need to use the *-i* or *-a* flags. When using these flags the report that is generated can be filtered down to specific IP or network addresses, ACLs, or a combination of both. All must be separated by a space and be either a valid address (no prefix or subnet mask supported), a valid ACL name on the ASA or a valid ACL name in the file (be careful with capitalization).

```bash
$python asa_acl_report_v3.py -d ste@10.10.10.1 -a data mgmt -i 10.10.20.254 10.10.10.71 10.10.10.50

========================== ASA ACL Auditor v0.3 (tested 9.8) ==========================
Checking the options entered are valid...
Enter the ASA password:
Gathering ACL info from the ASA...
Formatting the ACL data...
Creating the spreadsheet...
File /Users/mucholoco/10.10.10.1_ACLreport_20200311.xlsx has been created
```

## Error Handling

If any of the ASA login details are incorrect you will get a descriptive error message and be prompted to re-enter the password.

![image](https://user-images.githubusercontent.com/33333983/77829902-f3b57580-711c-11ea-8462-9f49cb3cd37b.png)

If the acl or acl_brief filename cannot located in the home directory you will be prompted to check and re-enter.

![image](https://user-images.githubusercontent.com/33333983/77829881-c5379a80-711c-11ea-93ec-732229362289.png)

If the destination filename entered already exists you will be prompted to ovewrite it or re-enter a new name.

![image](https://user-images.githubusercontent.com/33333983/77829760-0b402e80-711c-11ea-99ff-143a26f93676.png)

If the filtered IP address entered is not in a valid IPv4 format or the ACL does not exist (on the ASA or in the ACL file) the script will fail with details of the offending item or items.

<img width="762" alt="image" src="https://user-images.githubusercontent.com/33333983/69009348-4e0f2000-094c-11ea-84df-5f0c452ea441.png">

<img width="836" alt="image" src="https://user-images.githubusercontent.com/33333983/69008486-06d06180-0943-11ea-87a5-d1361d325bc9.png">

## Caveats

Only extended ACLs are supported, including standard ACLs wont break it they will just be ignored like remark statements.\
The script has been tested against the different ACE entry patterns I can think of and have come across. There maybe other patterns that I haven't thought about and missed, to fix any of these exceptions they would need to be added to section 4 (*Sanitize the data*) of the code.

## Unit testing

The unit testing is performed only on the parts of the script that require no remote device interaction using dummy files in the directory test/outputs. There is a separate test function for the user input data and one for formatting the ACL into XL ready format and adding the hit count timestamp.

```bash
pytest -v
pytest test/test_acl_report.py::test_data_mode -v
pytest test/test_acl_report.py::test_format_data -v
```
