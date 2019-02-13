#!/usr/bin/env python
"""
    Description: Generate space list for Confluence
    Author: Jackie Chen
    Version: 2019-01-31
"""

from __future__ import print_function
import http.cookiejar
import os
import sys
import json
import requests
requests.packages.urllib3.disable_warnings()


# Define your Confluence site
CONFLUENCE_URL = 'https://confluence.mydomain.com/'
API_URL = 'rest/api/'

# Report file location
FILE_PATH = '/jira_home/scripts/automation/confluence_picker/confluence_space_list'


# Pagination
def pagination(start):
    prefix_url = 'space?expand=name,description.plain&type=global&limit=100&start=' + start
    return prefix_url


# Get spaces
def get_spaces(username, password, url):
    return session.get(CONFLUENCE_URL + API_URL + url, auth=(username, password), verify=False)


# Parse spaces information
def parse_spaces(spaces):
    parsed_spaces = []
    for space in spaces:
        parsed_spaces.append(space['name'] + ' (' + space['key'] + ')')
    return parsed_spaces


# Generate spaces list report
def generate_report(spaces, report):
    with open(report, 'w') as f:
        for space in spaces:
            f.write(space.encode('utf-8') + '\n')


if __name__ == '__main__':
    session = requests.session()
    session.cookies = http.cookiejar.LWPCookieJar('cookie')
    spaces = []
    print("Downloading Space list from Confluence server...")
    for i in range(1, 1000, 100):
        print('Starting from ' + str(i) + '...')
        result = get_spaces(os.environ['USERNAME'], os.environ['PASSWORD'], pagination(str(i)))
        if result.status_code == 200:
            for result in json.loads(result.text)['results']:
                spaces.append(result)
        else:
            print('Login failed, exiting...')
            sys.exit()
    print('Generating Confluence space list report...')
    generate_report(parse_spaces(spaces), FILE_PATH)


