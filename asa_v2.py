
import os
from os.path import expanduser
import argparse
from pprint import pprint
from getpass import getpass
from netmiko import Netmiko
from ipaddress import ip_address


############# USER DEFINED VARIABLES #############
directory = expanduser("~")
report_name = 'asa_report'
device = 'ste@10.10.10.1'

# Optional flags user can enter to customise what is run, if nothing is entered uses the default options
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--filename', nargs='*', help="Name of a files (ACL and optionally acl brief) in 'directory' to run the script against.")
parser.add_argument('-d', '--device', default=device, help='Username and device (username@device) to run the script against (default: %(default)s)')
parser.add_argument('-i', '--ip', nargs='*', help='IP addresses or networks to filter on')
parser.add_argument('-a', '--acl', nargs='*', help='ACL names to filter on')
parser.add_argument('-l', '--location', default=directory, help='Location to save and run the report (default: %(default)s)')
parser.add_argument('-n', '--name', default=report_name, help='Name for the report (default: %(default)s)')
args = vars(parser.parse_args())

################################## 1. Validate info fed into the script ##################################

class Validate():
    def __init__(self):
        pass

# Verify the arguments entered are valid
    def verify_args(self):
        file_error, file_acl_error, asa_acls, acl_error, ip_error = ([] for i in range(5))
        against_asa = False         # Decides whether the ASA configuration or file is used for the input

        # FILENAME: Checks that the acl file and optionally the acl brief file exist, creates list of any that are not
        if args['filename'] != None:
            if not os.path.exists(os.path.join(directory, args['filename'][0])):
                file_error.append(os.path.join(directory, args['filename'][0]))
            if len(args['filename']) == 2:
                if not os.path.exists(os.path.join(directory, args['filename'][1])):
                    file_error.append(os.path.join(directory, args['filename'][1]))
            # Normalises file to remove non-ace lines
            if len(file_error) == 0:
                with open(os.path.join(directory, args['filename'][0])) as var:
                    file_acl = var.read().splitlines()
                    for ace in list(file_acl):
                        if (len(ace) == 0) or ('show' in ace) or ('access-list' not in ace) or ('elements' in ace) or ('cached' in ace) or ('remark' in ace):
                            file_acl.remove(ace)
                # Checks for hitcnt in ACL file (if missing is show run access-list)
                for ace in file_acl:
                    if 'hitcnt' not in ace:
                        file_acl_error.append(ace)
                # ACL: Makes sure that the ACL names entered exist in the file, creates list of any that are not
                if args['acl'] != None:
                    file_acls = []
                    for ace in file_acl:
                        y = ace.lstrip()
                        y = y.split(' ')
                        file_acls.append(y[1])
                    # Finds any specified ACLs not in the file
                    acl_error = set(args['acl']) - set(file_acls)

        # DEVICE: Validate device is reachable and the username and password are correct.
        elif args['filename'] == None:
            against_asa = True
            while True:
                try:
                    password = getpass('Enter the ASA password: ')
                    net_conn = Netmiko(host=device.split('@')[1], username=device.split('@')[0], password=password, device_type='cisco_asa')
                    net_conn.find_prompt()      # Expects to recieve prompt back from access switch
                    break
                except Exception as e:              # If login fails loops to begining with the error message
                    print(e)

            # ACL: Makes sure that the ACL names entered exist on the ASA, creates list of any that are not
            if args['acl'] != None:
                acl = net_conn.send_command('show run access-group')
                vpn_acl = net_conn.send_command('show run | in split-tunnel-network-list')
                for x in acl.splitlines():
                    asa_acls.append(x.split(' ')[1])
                for x in vpn_acl.splitlines():
                    asa_acls.append(x.split('value ')[1])
                # Converts to a 'set' to remove duplicates, then finds any specified ACLs not on ASA
                acl_error = set(args['acl']) - set(asa_acls)

        # IP: Makes sure the IP address are valid, if creates a list of non-valid IPs
        if args['ip'] != None:
            for ip_addr in args['ip']:
                try:
                    ip_address(ip_addr)
                except ValueError as errorCode:
                    ip_error.append(str(errorCode))

        # ERROR RESULTS: If any of the above generate errors (lists not empty) interact with user and kill the script
        if len(file_error) != 0:
             print('!!! ERROR - Invalid filenames entered, {} do not exist !!!'.format(file_error))
        if len(file_acl_error) !=0:
            print('!!! ERROR - No hitcnt in {}, make sure is output of "show RUN access-list" and NOT "show access-list" !!!'.format(args['filename'][0]))
        if len(acl_error) != 0:
            print("!!! ERROR - Invalid ACL names entered, {} are either not in the file or not ACLs on the ASA !!!".format(acl_error))
        if len(ip_error) != 0:
            print("!!!ERROR - The following IP address are not valid !!!")
            for x in ip_error:
                print(x)
        if len(file_error) != 0 or len(file_acl_error) !=0 or len(acl_error) != 0 or len(ip_error) != 0:
            exit()



# Unit test



  ################################## Gets or edits ACLs so only contain filtered IPs and ACLs ##################################

# !!!!!!!!! New function to gather ACLs !!!!!!!!!!!!!

# # 5a. ASA ONLY - Connects to the ASA and gathers the ACLs
# def get_acl(search_ips, acl_names):
#     acl = ''
#     # To get all ACL entries from all ACLs
#     if len(search_ips) == 0 and len(acl_names) == 0:
#         acl = net_conn.send_command('show access-list | ex elements|cached|alert-interval|remark')
#     # To get all ACL entries from specific ACLs
#     elif len(search_ips) == 0 and len(acl_names) != 0:
#         for x in acl_names:
#             acl = acl + net_conn.send_command('show access-list {}'.format(x))
#     # To get certain ACL entries from all acls
#     elif len(search_ips) != 0 and len(acl_names) == 0:
#         search_ips = '|'.join(search_ips)
#         acl = net_conn.send_command('show access-list | in {}'.format(search_ips))
#     # To get certain ACL entries from specific acls
#     elif len(search_ips) != 0 and len(acl_names) != 0:
#         search_ips = '|'.join(search_ips)
#         for x in acl_names:
#             acl = acl + net_conn.send_command('show access-list {} | in {}'.format(x, search_ips))
#     # Disconnect from ASA and run next function
#     net_conn.disconnect()
#     format_data(search_ips, acl_names, acl)


#         # Gather the hashes for all ACLs from show access-list brief
#         asa_acls = set(asa_acls)
#         acl_brief1 = ''
#         acl_brief = []
#         for x in asa_acls:
#             acl_brief1 = acl_brief1 + net_conn.send_command('show access-list {} brief'.format(x))
#         # Filter the output so only contains the hashes
#         for x in acl_brief1.splitlines():
#             if re.match(r"^\S{8}\s\S{8}\s", x):
#                 acl_brief.append(x)
#         # Run next function
#         get_acl(search_ips, acl_names)


# # 5b. FILE ONLY - Searches through the ACL file to filter only specified IPs and/or ACLs
# def filter_acl(search_ips, acl_names, acl1):
#     # To get all ACL entries from all ACLs
#     if len(search_ips) == 0 and len(acl_names) == 0:
#         acl = acl1
#     # To get certain ACL entries from specific acls
#     elif (len(acl_names) != 0) and (len(search_ips) != 0):
#         acl2 = []
#         for x in acl_names:
#             for y in acl1:
#                 if x in y:
#                     acl2.append(y)
#         acl = []
#         for x in search_ips:
#             for y in acl2:
#                 if x in y:
#                     acl.append(y)
#     # To get all ACL entries from specific ACLs
#     elif len(acl_names) != 0:
#         acl = []
#         for x in acl_names:
#             for y in acl1:
#                 if x in y:
#                     acl.append(y)
#     # To get certain ACL entries from all acls
#     elif len(search_ips) != 0:
#         acl = []
#         for x in search_ips:
#             for y in acl1:
#                 if x in y:
#                     acl.append(y)
#     # Converts the ACL file back from a list into a string and runs next function
#     acl = '\n'.join(acl)
#     format_data(search_ips, acl_names, acl)

#         # Grabs just lines with a hash from acl_brief by matching 8 characters, space, 8 characters
#         acl_brief = []
#         if len(acl_brief2) != 0:
#             with open(acl_brief2) as f:
#                 acl_brief1 = f.read().splitlines()
#             for x in acl_brief1:
#                 if re.match(r"^\S{8}\s\S{8}\s", x):
#                     acl_brief.append(x)
#         # Runs next function
#         filter_acl(search_ips, acl_names, acl1)



# ###################################### Run the scripts ######################################
# 1. Starts the script taking input of CSV file name

def main():
    print('\n' + '=' * 30, 'ASA ACL Auditor v0.3 (tested 9.6)', '=' * 30 + '\n')

    run = Validate()
    run.verify_args()



#     fname = argv[1]                                 # Creates varaible from the arg passed in when script run (csv file)
#     global csv_file
#     csv_file = os.path.join(directory, fname)       # Creates full path to the csv using directory variable
#     validation = Validate(csv_file)





if __name__ == '__main__':
    main()


# If want colours:
# from colorama import Fore, Back, Style, init
# print(Fore.GREEN + Style.BRIGHT + "!!!ERROR - The following IP address are not valid !!!")
# Put in documentaion and in the help file
#    print('This tool can be used to search specific IP addresses or all IPs in specific or all ACLs')
#     print("If searching against a file put all the ACLs in the one file. They must be expanded access-lists ('show access-list')")
#     print("To get the timestamp of last hit must have a second file with 'show access-list <name> brief' for the ACLs (optional)")

# python asa_acl_report.py -d <device> user -ip x.x.x.x -acl outside
# -f is file
# -d is device
# By default runs agaisnt a file called x in the test folder, does no filtering and saves the output in a file called x in the home directory (based on devicename or filename)


# Can enter as many


# If -ip used and no value prompts userf or list of ips seperated by space
# If -acl and no value prompts user for list of acls seperated by space
# If -ip and -acl prompts user for both ips and acls
# If none just doesnt prompt for nayhting to filter with

# Output in Excel rahter than CSV. Bold the tilte, make grey, maybe shade different ACLs.
# Create pytest for it


# When run with no flags will do both and save to a file called version_report in home directory.
# Use table for Table only, csv for CSV only, -l to change location, -f to change filename and -h for help


# # Optional flags user can enter to customise what is run, if nothing is entered uses the default options
# parser = argparse.ArgumentParser()
# parser.add_argument('output', default='both', nargs='?', choices=['csv', 'table', 'both'], help='Display a Table or Save as a CSV (default: %(default)s)')
# parser.add_argument('-f', '--filename', default=file_name, help='Name of the CSV (default: %(default)s)')
# parser.add_argument('-l', '--location', default=directory, help='Location to save the CSV (default: %(default)s)')
# args = vars(parser.parse_args())



