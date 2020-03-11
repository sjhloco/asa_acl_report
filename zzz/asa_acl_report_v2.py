#!/usr/bin/env python
# This script is to go through ASA access list (read from the device or a file) and produce human readable xl file.

import csv
import os
import re
from datetime import datetime
from os.path import expanduser
from sys import exit
import ipaddress
from ipaddress import IPv4Network
from getpass import getpass
from netmiko import Netmiko

################# Variables to change dependant on environment #################
# Sets it has users home directory
directory = expanduser("~")
# To change the default header values in the CSV file
csv_columns = ['ACL Name', 'Line Number', 'Access', 'Protocol', 'Source Address', 'Source Port',
               'Destination Address', 'Destination Port', 'Hit Count', 'Date Last Hit', 'Time Last Hit']

################################## Gather information from user ##################################
# 1. Welcome and informational screen
def start():
    global against_asa

    print()
    print('=' * 30, 'ASA ACL Auditor v0.2 (tested 9.6)', '=' * 30)
    print('This tool can be used to search specific IP addresses or all IPs in specific or all ACLs')
    print('If filtering IP addresses leave a blank space between entries')
    print('If filtering ACLs leave a blank space between entries and ensure capitliaztion is correct')
    print('The output will be stored in a CSV file saved in your the home directory')
    print()
    print('If searching against a file put all the ACLs in the one file. They must be expanded access-lists (show access-list)')
    print('To get the timestamp of last hit must have a second file with show access-list <name> brief for the ACLs (optional)')
    print('Both the ACL and ACL brief files should be stored in your home directory')
    print()
    # Options of whether to test against an ASA or a static file.
    while True:
        print('Do you want to grab the ACL config from an ASA or use a file?')
        print('1. Search against a ASA')
        print('2. Search against a file')
        answer = input('Type 1 or 2> ')
        if answer == '1':
            against_asa = True
            test_login()    # Test log into ASA
            break
        elif answer == '2':
            against_asa = False
            #gather_info()
            checks_files()   # Check files are valid
            break
        else:
            print('\n!!! ERROR - Response not understood, please try again !!!\n')

# 2a. ASA ONLY - Gets username/password and checks connectivity
def test_login():
    global net_conn             # Make connection variable global so can be used in all functions

    while True:
        try:
            device = input("Enter IP of the ASA firewall: ")
            username = input("Enter your username: ")
            password = getpass()
            net_conn = Netmiko(host=device, username=username, password=password, device_type='cisco_asa')
            net_conn.find_prompt()      # Expects to recieve prompt back from access switch
            break
        except Exception as e:              # If login fails loops to begining with the error message
            print(e)

    gather_info()                   # Runs next function

# 2b. FILE ONLY - Prompts user to enter the name of the files to be loaded. If cant find them prompts user to re-enter
def checks_files():
    global acl1, acl_brief2

    acl_file_exists = False
    acl_brief_file_exists = False
    print("\nThe results of show access-list and show access-list <name> brief must be in separate files.")
    print("Make sure that both files are already in your home directory before continuing.")

    while acl_file_exists is False:
        print("\nACL_FILE: Enter the full filename (including extension) of the file containing all the ACLs output.")
        filename = input('> ')
        filename = os.path.join(directory, filename)
        if not os.path.exists(filename):
            print('!!! ERROR - Cant find the file, was looking for {} !!!'.format(filename))
            print('Make sure it is in home directory and named correctly before trying again.')
        else:
            acl_file_exists = True

    while acl_brief_file_exists is False:
        print("\n-ACL_BR_FILE: Enter the full filename (including extension) of the file containing the ACL brief output (optional).")
        acl_brief2 = input('> ')
        if len(acl_brief2) != 0:
            acl_brief2 = os.path.join(directory, acl_brief2)
            if not os.path.exists(acl_brief2):
                print('!!! ERROR - Cant find the file, was looking for {} !!!'.format(acl_brief2))
                print('Make sure it is in home directory and named correctly before trying again.')
            else:
                acl_brief_file_exists = True
        else:
            acl_brief_file_exists = True

    # Runs checks against the ACL file to make sure is valid and normalizes it
    with open(filename) as var:
        acl1 = var.read().splitlines()
    # Remove all lines that arent ACEs
    for x in list(acl1):
        if (len(x) == 0) or ('show' in x) or ('access-list' not in x) or ('elements' in x) or ('cached' in x) or ('remark' in x):
            acl1.remove(x)
    # Exits script if no hitcnt as means user has done show run access-list
    for x in acl1:
        if 'hitcnt' not in x:
            print('!!! ERROR - No hitcnt in {}, the file is incompatible with this script !!!'.format(filename))
            print('Check the file and make sure you have done "show access-list" and NOT "show RUN access-list"')
            exit()

    gather_info()                   # Runs next function

# 3. Gathers the IP addresses and ACLs Names to be filtered as well as the name to use for the CSV file
def gather_info():
    global filename
    # Prompts user to enter the IPs to be searched and makes a list of them.
    print("\nIP: Enter the IPs you want to search for in the ACLs separated by a space. Leave blank to search all IPs.")
    ips_entered = input('> ')
    search_ips = []
    if len(ips_entered) != 0:
        search_ips = ips_entered.split(' ')

    # Prompts user to enter the ACLs to be searched and makes a list of them.
    print("\nACL: Enter the names of the ACLs you want to search in separated by a space. Leave blank to search all ACLs.")
    acls_entered = input('> ')
    acl_names = []
    if len(acls_entered) != 0:
        acl_names = acls_entered.split(' ')

    # Prompts user to enter the name of the file to be created. It it already exists prompts user to confirm they want to overwrite.
    while True:
        print("\nFILE: Enter the name of the file to save the results to.")
        filename = input('> ')
        filename = os.path.join(directory, filename + ".csv")
        if os.path.exists(filename):
            print("The filename already exists, do you want to overwrite this?")
            print("Type y if this is correct, or n to re-enter the file name.")
            answer = input('> ')
            if answer == 'y':
                break
        else:
            break
    # Run next function
    verify(search_ips, acl_names)

################################## Validates entered information and gets ACLs/ ACL brief from ASA or file ##################################
# 4. Verifies that the entered filter information is of a valid format
def verify(search_ips, acl_names):
    global acl_brief
    ip_error = []
    acl_error = []

    # Checks to make sure that the IP address are valid, if not exits the script
    if len(search_ips) != 0:
        for ip in search_ips:
            # Checks if IPs are valid, gathers list of non-valid IPs
            try:
                ipaddress.ip_address(ip)
            except ValueError as errorCode:
                ip_error.append(str(errorCode))
    # Exits script if there was an ip address error (list not empty)
    if len(ip_error) != 0:
        print("!!!ERROR - Invalid IP addresses entered !!!")
        for x in ip_error:
            print(x)
        exit()

    # ASA ONLY - Checks to make sure that the ACL names are on the ASA, if not exits the script
    if against_asa is True:
        # Gathers list of access-group ACLs and group policy ACLs
        asa_acls = []
        acl = net_conn.send_command('show run access-group')
        vpn_acl = net_conn.send_command('show run | in split-tunnel-network-list')
        for x in acl.splitlines():
            asa_acls.append(x.split(' ')[1])
        for x in vpn_acl.splitlines():
            asa_acls.append(x.split('value ')[1])

        # If user entered a list of ACLs checks to make sure they are on the ASA
        if len(acl_names) != 0:
            # Converts to a set to remove duplicates, then finds any element from acl_names not in acls
            acl_error = list(set(acl_names) - set(asa_acls))
            # Exits script if there was an acl name error (list not empty)
            if len(acl_error) != 0:
                print("!!! ERROR - Invalid ACL names entered !!!")
                for x in acl_error:
                    print("'{}' does not appear to be an ACL on the ASA".format(x))
                exit()
        # Gather the hashes for all ACLs from show access-list brief
        asa_acls = set(asa_acls)
        acl_brief1 = ''
        acl_brief = []
        for x in asa_acls:
            acl_brief1 = acl_brief1 + net_conn.send_command('show access-list {} brief'.format(x))
        # Filter the output so only contains the hashes
        for x in acl_brief1.splitlines():
            if re.match(r"^\S{8}\s\S{8}\s", x):
                acl_brief.append(x)
        # Run next function
        get_acl(search_ips, acl_names)

    # FILE ONLY - Creates a list of ACL names from the acl file to compare against the user entered ACL names
    elif against_asa is False:
        file_acls = []
        for x in acl1:
            y = x.lstrip()
            y = y.split(' ')
            file_acls.append(y[1])
        # Converts to a set to remove duplicates, then finds any element from acl_names not in acls
        acl_error = list(set(acl_names) - set(file_acls))
        # Exits script if there was an acl name error (list not empty)
        if len(acl_error) != 0:
            print("!!! ERROR - Invalid ACL names entered !!!")
            for x in acl_error:
                print("'{}' does not appear to be an ACL in the file".format(x))
                exit()

        # Grabs just lines with a hash from acl_brief by matching 8 characters, space, 8 characters
        acl_brief = []
        if len(acl_brief2) != 0:
            with open(acl_brief2) as f:
                acl_brief1 = f.read().splitlines()
            for x in acl_brief1:
                if re.match(r"^\S{8}\s\S{8}\s", x):
                    acl_brief.append(x)
        # Runs next function
        filter_acl(search_ips, acl_names, acl1)

################################## Gets or edits ACLs so only contain filtered IPs and ACLs ##################################
# 5a. ASA ONLY - Connects to the ASA and gathers the ACLs
def get_acl(search_ips, acl_names):
    acl = ''
    # To get all ACL entries from all ACLs
    if len(search_ips) == 0 and len(acl_names) == 0:
        acl = net_conn.send_command('show access-list | ex elements|cached|alert-interval|remark')
    # To get all ACL entries from specific ACLs
    elif len(search_ips) == 0 and len(acl_names) != 0:
        for x in acl_names:
            acl = acl + net_conn.send_command('show access-list {}'.format(x))
    # To get certain ACL entries from all acls
    elif len(search_ips) != 0 and len(acl_names) == 0:
        search_ips = '|'.join(search_ips)
        acl = net_conn.send_command('show access-list | in {}'.format(search_ips))
    # To get certain ACL entries from specific acls
    elif len(search_ips) != 0 and len(acl_names) != 0:
        search_ips = '|'.join(search_ips)
        for x in acl_names:
            acl = acl + net_conn.send_command('show access-list {} | in {}'.format(x, search_ips))
    # Disconnect from ASA and run next function
    net_conn.disconnect()
    format_data(search_ips, acl_names, acl)

# 5b. FILE ONLY - Searches through the ACL file to filter only specified IPs and/or ACLs
def filter_acl(search_ips, acl_names, acl1):
    # To get all ACL entries from all ACLs
    if len(search_ips) == 0 and len(acl_names) == 0:
        acl = acl1
    # To get certain ACL entries from specific acls
    elif (len(acl_names) != 0) and (len(search_ips) != 0):
        acl2 = []
        for x in acl_names:
            for y in acl1:
                if x in y:
                    acl2.append(y)
        acl = []
        for x in search_ips:
            for y in acl2:
                if x in y:
                    acl.append(y)
    # To get all ACL entries from specific ACLs
    elif len(acl_names) != 0:
        acl = []
        for x in acl_names:
            for y in acl1:
                if x in y:
                    acl.append(y)
    # To get certain ACL entries from all acls
    elif len(search_ips) != 0:
        acl = []
        for x in search_ips:
            for y in acl1:
                if x in y:
                    acl.append(y)
    # Converts the ACL file back from a list into a string and runs next function
    acl = '\n'.join(acl)
    format_data(search_ips, acl_names, acl)

################################## Sanitize the data - Create structured data ##################################
def format_data(search_ips, acl_names, acl):
    # 4. Pad out any and remove hitcnt text by replacing fields. Is all done whilst file is one big string
    acl = acl.replace('any4', 'any')    # Incase any4 acls used for packet captures
    acl = acl.replace('any', 'any any1')
    for elem in ['(hitcnt=', ')']:
        acl = acl.replace(elem, '')

    # 5. Clean up ACL by removing remarks and informational data (from ASA output, file was already done)
    acl = acl.splitlines()
    for x in list(acl):
        if ('elements' in x) or ('cached' in x) or ('alert-interval' in x) or ('remark' in x) or (len(x) == 0):
            acl.remove(x)
    # 6. Remove unneeded fields, lines with object-group in and logging
    acl1 = []
    for x in acl:
        if 'object-group' not in x:     # Remove all lines with object-group
            y = x.strip()               # Removes all starting and trailing whitespaces
            y = y.split(' ')
            for z in [0, 1, 2]:         # Deletes access-list, line and extended
                del y[z]
            if 'log' in y:              # If ACL is logging removes log and 3 fields after (log notifications interval 300)
                del y[-6:-2]
            acl1.append(y)

    # 7. Now got only data we need normalise source ports by joining range, removing eq and padding out if is no source port
    acl2 = []
    for b in acl1:
        if b[6] == 'range':             # If has a source range of ports replace "range" with "start-end" port numbers
            c = b.pop(7)
            d = b.pop(7)
            b[6] = c + '-' + d
        elif b[6] == 'eq':              # If has a single source port delete eq
            del b[6]
        elif 'icmp' not in b:           # If it is not ICMP and has no source port padout with any_port
            (b.insert(6, 'any_port'))
        else:
            if ('.' in b[6]) or (b[6] == 'any'):        # If ICMP has no port padout with any_port
                (b.insert(6, 'any_port'))
        acl2.append(b)
    # 8. Normalise destination ports by joining range, removing eq and padding out if no source port.
    acl3 = []
    for b in acl2:
        if 'range' in b:
            c = b.pop(-4)
            d = b.pop(-3)
            b[-3] = c + '-' + d
        elif 'eq' in b:
            del b[-4]
        elif 'icmp' not in b:
            (b.insert(-2, 'any_port'))
        else:
            if ('.' in b[-3]) or (b[-3] == 'any1'):
                (b.insert(-2, 'any_port'))
        acl3.append(b)

    # 9. For all host entries delete host and add /32 subnet mask after the IP
    acl4 = []
    for x in acl3:
        if x[4] == 'host':
            del x[4]
            (x.insert(5, '255.255.255.255'))
        if x[7] == 'host':
            del x[7]
            (x.insert(8, '255.255.255.255'))
        acl4.append(x)

    # 10. Convert subnet mask to prefix and padout old mask with 'any1'
    for x in acl4:
        if x[4] != 'any':
            y = IPv4Network((x[4], x[5])).with_prefixlen
            x[4] = y
            x[5] = 'any1'
        if x[7] != 'any':
            y = IPv4Network((x[7], x[8])).with_prefixlen
            x[7] = y
            x[8] = 'any1'
        del x[5]        # Delete the 'any1' padding that was used earlier
        del x[7]
    lasthit_time(acl4)

# 11. Adds date and time for last hit for any ACEs with a hitcnt. This info is got as unix hash from last element in show access-list <name> brief
def lasthit_time(acl4):
    # If ACE has a matching hash entry (has a hitcnt) last hit date and time will be added
    for lines in acl4:              # loop through ACL
        for hashes in acl_brief:     # Loop through acl_brief
            if hashes.split(' ')[0] in lines[-1]:    # If hash is in acl
                unix_time = hashes.split(' ')[-1]
                # Convert last element to decimal and get human-readable time from the hex time
                human_time = datetime.fromtimestamp(int(unix_time, 16)).strftime('%Y-%m-%d %H:%M:%S').split(' ')
                lines[-1] = human_time[0]
                lines.append(human_time[1])
    # If ACE does not have a matching hash entry hash is stripped out
    for lines in acl4:
        if len(lines) == 10:
            del lines[-1]
    create_csv(acl4)

# 12. Create CSV from the output using the header Fields in the global variables at the beginning
def create_csv(acl4):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(csv_columns)
        for data in acl4:
            writer.writerow(data)
    print()
    print('File {} has been created'.format(filename))

# 13. Starts the script
start()

################################## Run or test elements of script ##################################

#### Test ASA run but skip entering login details
#net_conn = Netmiko(host='10.10.10.1', username='ste', password='xxx', device_type='cisco_asa')
#against_asa = True
#gather_info()
