# From the named script import the functions to be tested
from asa_acl_report_v3 import Validate
from asa_acl_report_v3 import Format_data
import os
import pytest

################# Variables to change dependant on environment #################
directory = os.path.join(os.path.dirname(__file__), 'outputs')    # CSV file location, use __file__ to start from same directory as test scripts

test_data_model_args = {'acl': ['outside', 'data', 'mgmt'], 'device': None, 'filename': ['acl_filter', 'acl_brief'],
                        'ip': ['10.10.20.254', '10.10.10.51'], 'location': directory, 'name': 'asa_report'}
test_format_data_args = {'acl': None, 'device': None, 'filename': ['acl_format', 'acl_brief'], 'ip': None, 'location': directory, 'name': 'asa_report'}

# Tests input data is validated correctly and filtered ACL captured
def test_data_model():
    test = Validate(test_data_model_args)
    input_args = test.verify_args()
    acl_data = test.get_filter_acl()
    assert input_args == [['acl_filter', 'acl_brief'], ['10.10.20.254', '10.10.10.51'], ['outside', 'data', 'mgmt'],
                           '/Users/mucholoco/Documents/Coding/Python/code/asa_acl_report/test/outputs']
    assert acl_data == ['access-list outside line 10 extended permit udp object-group FIREWALLS host ' '10.10.20.254 eq domain (hitcnt=0) 0xb5663c34\n'
                        '  access-list outside line 10 extended permit udp host 172.168.255.2 host ' '10.10.20.254 eq domain (hitcnt=0) 0xf3128096\n'
                        '  access-list outside line 10 extended permit udp host 172.168.255.4 host ' '10.10.20.254 eq domain (hitcnt=0) 0x88a7cae6\n'
                        '  access-list outside line 10 extended permit udp 10.10.50.0 255.255.255.0 ' 'host 10.10.20.254 eq domain (hitcnt=0) 0x9705b667\n'
                        '  access-list outside line 10 extended permit udp 10.10.60.0 255.255.252.0 ' 'host 10.10.20.254 eq domain (hitcnt=0) 0x45935a8f\n'
                        '  access-list outside line 10 extended permit udp host 172.168.255.3 host ' '10.10.20.254 eq domain (hitcnt=0) 0x681ee92d\n'
                        'access-list mgmt line 2 extended permit icmp any host 10.10.20.254 echo ' '(hitcnt=13759) 0x4d69e4a3\n'
                        'access-list mgmt line 9 extended permit udp any host 10.10.20.254 eq domain ' '(hitcnt=1342378) 0xbedb9398\n'
                        'access-list outside line 11 extended permit udp object-group FIREWALLS host ' '10.10.10.51 eq ntp (hitcnt=1461) 0xd7f06497\n'
                        '  access-list outside line 11 extended permit udp host 172.168.255.2 host ' '10.10.10.51 eq ntp (hitcnt=0) 0x42d34a9b\n'
                        '  access-list outside line 11 extended permit udp host 172.168.255.4 host ' '10.10.10.51 eq ntp (hitcnt=1461) 0x494e5d6c\n'
                        '  access-list outside line 11 extended permit udp 10.10.50.0 255.255.255.0 ' 'host 10.10.10.51 eq ntp (hitcnt=0) 0x551a4552\n'
                        '  access-list outside line 11 extended permit udp 10.10.60.0 255.255.252.0 ' 'host 10.10.10.51 eq ntp (hitcnt=0) 0xf28ba1a0\n'
                        '  access-list outside line 11 extended permit udp host 172.168.255.3 host ' '10.10.10.51 eq ntp (hitcnt=0) 0x5dd96e0e',
                       ['4d69e4a3 00000000 000035bf 5e56e683',  '4c1d46ce 00000000 00000b93 5e62cb04',  'bedb9398 00000000 00147c01 5e62cb1e',
                        '58e5e5a9 00000000 000561e9 5e62cb23',  '4931fac3 f081f39e 00006128 5e6047e5',  '2e290047 f081f39e 0000eb70 5e62cb27',
                        '92a1d35a 00000000 00000f4d 5e62b795',  'db487564 00000000 00000764 5e604b0d',  '83d4ea4f 00000000 0000097e 5e61bd05',
                        '494e5d6c d7f06497 000005b5 5e56d514',  'fe8f010b 00000000 0000001e 5e559ce6',  '48291ccf 00000000 00000521 5e56d6b2',
                        'fd0ffa4a 00000000 01569203 5e62cb53',  '17e1b5ee 00000000 0000000f 5e55cff8',  '459af468 00000000 000004cb 5e56c580']]

def test_format_data():
    test = Validate(test_format_data_args)
    test.verify_args()
    acl_data = test.get_filter_acl()
    test1 = Format_data(acl_data)

    acl = test1.format_acl()
    assert acl == [['stecap',  '1',  'permit',  'ip',  'any',  'any_port',  'any',  'any_port',  '0',  '0xeb4dc6c7'],
                   ['stecap',  '2',  'permit',  'tcp',  '10.10.10.0/32',  'any_port',  'any',  '443',  '0',  '0xeb4dc6c2'],
                   ['stecap',  '2',  'permit',  'tcp',  'any',  'any_port',  '10.10.10.0/24',  '443',  '0',  '0xeb4dc6c3'],
                   ['mgmt',  '2',  'permit',  'icmp',  'any',  'any_port',  'any',  'echo',  '13759',  '0x4d69e4a3'],
                   ['mgmt',  '3',  'permit',  'icmp',  '1.1.1.1/32',  'any_port',  'any',  'echo-reply',  '0',  '0x4ce78373'],
                   ['mgmt',  '4',  'permit',  'icmp',  'any',  'any_port',  '2.2.2.2/32',  'unreachable',  '3028',  '0x4c1d46ce'],
                   ['mgmt',  '5',  'permit',  'icmp',  '10.10.10.0/24',  'any_port',  'any',  'time-exceeded',  '0',  '0x6bc9ea44'],
                   ['mgmt',  '5',  'permit',  'icmp',  'any',  'any_port',  '10.10.10.0/24',  'time-exceeded',  '0',  '0x6bc9ea44'],
                   ['mgmt',  '6',  'deny',  'icmp',  'any',  'any_port',  'any',  'any_port',  '0',  '0x2b138472'],
                   ['mgmt',  '9',  'permit',  'tcp',  '10.10.10.1/32',  '67-68',  '20.20.20.1/32',  '67-68',  '0',  '0x4ce78374'],
                   ['mgmt',  '10',  'permit',  'tcp',  'any',  '22',  '20.20.20.0/24',  '67-68',  '9222',  '0xe6001f54'],
                   ['mgmt',  '11',  'permit',  'tcp',  '10.10.10.1/32',  '67-68',  'any',  '22',  '0',  '0x4ce78378'],
                   ['mgmt',  '12',  'permit',  'tcp',  '20.20.20.0/24',  '22',  'any',  '22',  '1227',  '0x459af468'],
                   ['outside',  '2',  'deny',  'tcp',  'any',  'www',  'any',  'any_port',  '0',  '0x380c90d9'],
                   ['outside',  '2',  'deny',  'tcp',  'any',  'https',  'any',  'any_port',  '0',  '0xb29d4647'],
                   ['outside',  '3',  'deny',  'ip',  'any',  'any_port',  '10.10.10.0/24',  'any_port',  '24876',  '0x4931fac3'],
                   ['outside',  '3',  'deny',  'ip',  'any',  'any_port',  '10.10.20.0/24',  'any_port',  '0',  '0xe0db7aa9']]

    final_acl = test1.lasthit_time(acl)
    assert final_acl == [['stecap', '1', 'permit', 'ip', 'any', 'any_port', 'any', 'any_port', '0'],
                         ['stecap',  '2',  'permit',  'tcp',  '10.10.10.0/32',  'any_port',  'any',  '443',  '0'],
                         ['stecap',  '2',  'permit',  'tcp',  'any',  'any_port',  '10.10.10.0/24',  '443',  '0'],
                         ['mgmt',  '2',  'permit',  'icmp',  'any',  'any_port',  'any',  'echo',  '13759',  '2020-02-26',  '21:43:31'],
                         ['mgmt',  '3',  'permit',  'icmp',  '1.1.1.1/32',  'any_port',  'any',  'echo-reply',  '0'],
                         ['mgmt',  '4',  'permit',  'icmp',  'any',  'any_port',  '2.2.2.2/32',  'unreachable',  '3028',  '2020-03-06',  '22:13:24'],
                         ['mgmt',  '5',  'permit',  'icmp',  '10.10.10.0/24',  'any_port',  'any',  'time-exceeded',  '0'],
                         ['mgmt',  '5',  'permit',  'icmp',  'any',  'any_port',  '10.10.10.0/24',  'time-exceeded',  '0'],
                         ['mgmt', '6', 'deny', 'icmp', 'any', 'any_port', 'any', 'any_port', '0'],
                         ['mgmt',  '9',  'permit',  'tcp',  '10.10.10.1/32',  '67-68',  '20.20.20.1/32',  '67-68',  '0'],
                         ['mgmt', '10', 'permit', 'tcp', 'any', '22', '20.20.20.0/24', '67-68', '9222'],
                         ['mgmt', '11', 'permit', 'tcp', '10.10.10.1/32', '67-68', 'any', '22', '0'],
                         ['mgmt',  '12',  'permit',  'tcp',  '20.20.20.0/24',  '22',  'any',  '22',  '1227',  '2020-02-26',  '19:22:40'],
                         ['outside', '2', 'deny', 'tcp', 'any', 'www', 'any', 'any_port', '0'],
                         ['outside', '2', 'deny', 'tcp', 'any', 'https', 'any', 'any_port', '0'],
                         ['outside',  '3',  'deny',  'ip',  'any',  'any_port',  '10.10.10.0/24',  'any_port',  '24876',  '2020-03-05',  '00:29:25'],
                         ['outside',  '3',  'deny',  'ip',  'any',  'any_port',  '10.10.20.0/24',  'any_port',  '0']]