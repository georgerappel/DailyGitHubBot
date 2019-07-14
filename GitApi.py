#!/usr/bin/env python
# -*- coding:utf-8 -*-

from datetime import datetime, timedelta
from json import loads
from requests import get


class GitHub:

    def __init__(self, config):
        self.msg = ""
        self.config = config

    def url_parameters(self):
        params = '?sort=pushed&direction=desc'

        try:
            # Configuration file
            if self.config['DEFAULT']['client_id'] is not None and self.config['DEFAULT']['client_secret'] is not None:
                params += '&client_id=' + self.config['DEFAULT']['client_id']
                params += '&client_secret=' + self.config['DEFAULT']['client_secret']
        except Exception as e:
            print("Error trying to get api config: ")
            print(e)

        return params

    # List repositories for an Organzation (up to 30)
    def get_org_repos(self, organization):
        self.msg = ""
        req = loads(get('https://api.github.com/orgs/' + organization + '/repos' + self.url_parameters()).text)
        self.msg += '\nRepositories.'
        for i in range(len(req)):
            self.msg += '\n\n[' + str(req[i]['name']) + '](' + str(req[i]['html_url']) + ')'  # Name with URL
            self.msg += '\n\U0001F4C4 ' + str(req[i]['description'])

        return self.msg

    # Count commits today for an organization
    def get_org_today(self, organization):
        self.msg = ""
        commit_count = 0
        repo_count = 0
        today = datetime.now()
        yesterday = (today - timedelta(1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        url = 'https://api.github.com/orgs/' + organization + '/repos' + self.url_parameters()
        req = loads(get(url).text)
        for i in range(len(req)):
            pushed_at = datetime.strptime(req[i]['pushed_at'], "%Y-%m-%dT%H:%M:%SZ")
            diff = datetime.now() - pushed_at
            if diff.days < 1:
                req2 = loads(get('https://api.github.com/repos/' + organization + '/' + req[i]['name']
                                 + '/commits?since=' + yesterday).text)
                if len(req2) > 0:
                    self.msg += '\n' + str(req[i]['name']) + ': ' + str(len(req2)) + ' commits'
                    commit_count += len(req2)
                    repo_count += 1

        if commit_count > 0:
            self.msg = "Repositories updated today: " + str(repo_count) + " with " + str(commit_count) + " commits!\n" \
                       + self.msg
        else:
            self.msg = "No repositories were updated today."

        return self.msg


if __name__ == "__main__":
    arg = GitHub()
