# ASA ACL Report

ASA ACL Auditer v0.2 (tested 9.6)

This tool will create a CSV file of the ACLs on an ASA with details of the hit counts and the last time the rule was hit. The results can be filtered down to a specific subset of ACLs and addresses.

IMAGE

The report can either be generated from the ASA or offline and run against previously extracted command outputs.
To run offline you need to collect the following information and save in separate files in your home directory:
**-ACLs** *(mandatory)*: All the expanded access-lists (*show access-list*) you wish to evaluate against stored in the 1 single file.
**-ACL Brief** *(optional)*: To get the timestamp of the last hit must have a second file with *show access-list <name> brief* for the ACLs. Any ACLs without this file you will not get the timestamp information in the csv.

## Prerequisites

