#!/usr/bin/env python
"""
    Description: Generate project list for Jira
    Author: Jackie Chen
    Version: 2019-01-31
"""

from __future__ import print_function
import http.cookiejar
import sys
import os
import json
import requests
requests.packages.urllib3.disable_warnings()

# Define your Jira site
JIRA_URL = 'https://jira.mydomain.com/'
API_URL = 'rest/api/2/'
PREFIX_URL = 'project?expand=name,description'

# Report file location
FILE_PATH = '/jira_home/scripts/automation/jira_picker/jira_project_list'


# Get project list
def get_projects(username, password):
    print("Downloading project list from Jira server....")
    return session.get(JIRA_URL + API_URL + PREFIX_URL, auth=(username, password), verify=False)


# Parse project information
def parse_projects(projects):
    parsed_projects = []
    for project in projects:
        parsed_projects.append(project['name'] + ' (' + project['key'] + ')')
    return parsed_projects


# Generate projects list report
def generate_report(projects, report):
    with open(report, 'w') as f:
        for project in projects:
            f.write(project.encode('utf-8') + '\n')


if __name__ == '__main__':
    session = requests.session()
    session.cookies = http.cookiejar.LWPCookieJar('cookie')
    result = get_projects(os.environ['USERNAME'], os.environ['PASSWORD'])
    if result.status_code == 200:
        print('Generating Jira project list report...')
        generate_report(parse_projects(json.loads(result.text)), FILE_PATH)
    else:
        print('Login failed, exiting...')
        sys.exit()


