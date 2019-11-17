# ASA ACL Report

ASA ACL Auditor v0.3 (tested 9.6)

Creates a CSV file of the ACLs on an ASA with details of the hit counts and the last time the rule was hit. The results can be filtered down to a specific subset of ACLs and addresses.

![image](https://user-images.githubusercontent.com/33333983/69008082-36c93600-093e-11ea-9fcf-7d795248108f.png)

The report can either be generated from the ASA or generated offline by running against previously extracted command outputs. To run offline you need to collect the following info and save it in separate files in your home directory:

- **ACLs** *(mandatory)*: All the expanded access-lists (*show access-list*) you wish to evaluate against stored in the one single file.
- **ACL Brief** *(optional)*: To get the timestamp of the last hit you must have a second file with *show access-list <name> brief* for the ACLs. Any ACLs without this file you will not get the timestamp information in the csv.

## Prerequisites

The only extra package required to run this is netmiko, itis used for the SSH connections to the device.
```
pip install -r requirements.txt
```

The first section of the script is the customisable variables. You can change the default directory location (where it saves the CSV and looks for offline files) and the CSV header names.
```
directory = expanduser("~")
csv_columns = ['ACL Name', 'Line Number', 'Access', 'Protocol', 'Source Address', 'Source Port',
               'Destination Address', 'Destination Port', 'Hit Count', 'Date Last Hit', 'Time Last Hit']
```

## Usage

The info gathered in the script is all done from user interaction once the script has been run. To get started enter:
```
python asa_acl_report.py
```

<img width="819" alt="image" src="https://user-images.githubusercontent.com/33333983/69007995-52800c80-093d-11ea-970a-191c5f8b194b.png">

### Run against ASA
When running against a device the IP adddress, username and password are required.

<img width="809" alt="image" src="https://user-images.githubusercontent.com/33333983/69008179-84926e00-093f-11ea-8669-3644036069d8.png">

### Run against File
When running against files you must specify the full filename (including extensions) and the script will by default look in your home directory for them. The files will be sanitized to remove any unneeded blank lines and commands as well as ensuring that it is not the output of *show run access-list*.

<img width="836" alt="image" src="https://user-images.githubusercontent.com/33333983/69008920-fa9ad300-0947-11ea-8595-711a10b0744b.png">

### Results
If you only want a full list of all ACEs in all the ACLs you can leave the the next two options blank and just enter the filename where the results will be stored.

<img width="840" alt="image" src="https://user-images.githubusercontent.com/33333983/69008932-23bb6380-0948-11ea-9555-d9bee32c6fb6.png">

## Filtering
The report that is generated can be filtered down to specific addresses, ACLs, or a combination of both. All must be separated by a space and be either a valid address (no prefix or subnet mask supported) or a valid ACL name on the ASA (be careful with capitalization).

![image](https://user-images.githubusercontent.com/33333983/69008956-5ebd9700-0948-11ea-99fd-12cecb4c0125.png)

## Error Handling
If any of the ASA login details are incorrect you will get a descriptive error message and be prompted to re-enter.

<img width="822" alt="image" src="https://user-images.githubusercontent.com/33333983/69008411-10a59500-0942-11ea-92a2-40631cce221f.png">

If the acl or acl_breif filename cannot located in the home directory you will be prompted to check and re-enter.

<img width="699" alt="image" src="https://user-images.githubusercontent.com/33333983/69008279-9de7ea00-0940-11ea-95d4-9800d7b04cea.png">

If the filename entered already exists you will be prompted to ovewrite it or re-enter a new name.

<img width="801" alt="image" src="https://user-images.githubusercontent.com/33333983/69008332-236b9a00-0941-11ea-8a65-2ca69d9c454e.png">

If the address entered is not in a valid IPv4 format or the ACL does not exist (on the ASA or in the ACL file) the script will fail with details of the offending item.

<img width="801" alt="image" src="https://user-images.githubusercontent.com/33333983/69008476-e1dbee80-0942-11ea-89a7-bb5ea84f11d4.png">

<img width="836" alt="image" src="https://user-images.githubusercontent.com/33333983/69008486-06d06180-0943-11ea-87a5-d1361d325bc9.png">
