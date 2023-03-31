#!/usr/bin/env python3
#
#  Author: VCNTQA
#  Date: 2023-03-14 (Tue, 14 Mar 2023)
#  Version: 1.0
#  Parameters:
#    - data domain name

"""
Nagios plugin to get storage domain size from Oracle Linux Virtualization Manager via REST API.

Can optionally alert on available size by setting metric with format metric_name=valueunit;warning_threshold;critical_threshold;min_value;max_value
(check https://docs.centreon.com/docs/reporting/concepts/ for more details.)
"""

# Import pacakges
import requests
from requests.exceptions import ConnectTimeout
import json
import sys
import xml.etree.ElementTree as ET

import warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
warnings.simplefilter('ignore',InsecureRequestWarning)

# Standard return codes
OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3

DEFAULT_TIMEOUT_SECONDS = 30

# OLVM manager url and certificate
# check https://www.ovirt.org/documentation/doc-REST_API_Guide/#obtaining-the-ca-certificate for more details to obtain OLVM certificate:
URL_base = 'https://olvmmanager.domain.com'                            # OLVM Manager URL
CA_path = '/etc/pki/ovirt-engine/ca.pem'                               # OLVM certificate location
Headers_session = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': 'Basic HjezghdLjfhjHarepCkldqerogsmvYkchslpamd',  # Basic64 authorization
}

# Pass parameter (data domain name) from Centreon to script
try:
    storage_domain_name     = sys.argv[1]
except:
    output    = f'CRITICAL! Please provide the storage domain name.'
    print(output)
    sys.exit(CRITICAL)

# Get request 
URL_session   = f'{URL_base}/ovirt-engine/api/storagedomains'
try:
    r_session = requests.get(URL_session, headers=Headers_session, verify=CA_path, timeout=DEFAULT_TIMEOUT_SECONDS)
except ConnectTimeout:
    output    = f'CRITICAL: Request has timed out after {DEFAULT_TIMEOUT_SECONDS} seconds.'
    print(output)
    sys.exit(CRITICAL)

if r_session.status_code != requests.codes['ok']:
    output   = f'CRITICAL: {r_session.status_code} {r_session.reason}'
    print(output)
    sys.exit(CRITICAL)

# Get storage_domain information
try:
    storage_domain = r_session.json()['storage_domain']
except:
    output   = f'CRITICAL: {r_session.status_code} Cannot parse storage_domain.'
    print(output)
    sys.exit(CRITICAL)

# Search storage domain with specified name
for domain in storage_domain:
    if domain['name'].lower() == storage_domain_name.lower():
        used_size_GB      = int(domain['used'])/1024/1024/1024
        available_size_GB = int(domain['available'])/1024/1024/1024

if used_size_GB != None and available_size_GB != None:
    output   = f'Storage Domain {storage_domain_name} available space {available_size_GB} GB and used space {used_size_GB} GB | available_space={available_size_GB}GB;;;; used_space={used_size_GB}GB;;;;'
    exit_code = OK
else:
    output   = f'CRITICAL: Storage Domain {storage_domain_name} not found'
    exit_code = CRITICAL

# Return result to Centreon
print(output)
sys.exit(exit_code)
