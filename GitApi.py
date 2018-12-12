#!/usr/bin/env python
# -*- coding:utf-8 -*-

from requests import get
from json import loads
from argparse import ArgumentParser
from datetime import datetime, timedelta
from time import time

class GitHub:

    def get_org_repos(self, organization):
        self.msg = ""
        req = loads(get('https://api.github.com/orgs/' +
                        organization + '/repos').text)
        self.msg += '\nRepositories.'
        for i in range(len(req)):
            self.msg += '\n\nName: ' + str(req[i]['name'])
            self.msg += '\nDescription: ' + \
                str(req[i]['description'])
            self.msg += '\nURL repository: ' + str(req[i]['html_url'])
            self.msg += '\nStars: total: ' + \
                str(req[i]['stargazers_count'])
            self.msg += '\nForks total: ' + \
                str(req[i]['forks_count'])
        return self.msg

    def get_org_today(self, organization):
        self.msg = ""
        commit_count = 0
        repo_count = 0
        today = datetime.now()
        tempo = time()
        yesterday = (today - timedelta(1)).strftime("%Y-%m-%dT%H:%M:%SZ")

        req = loads(get('https://api.github.com/orgs/' +
                        organization + '/repos').text)
        for i in range(len(req)):
            pushed_at = datetime.strptime(req[i]['pushed_at'], "%Y-%m-%dT%H:%M:%SZ")
            diff = datetime.now() - pushed_at
            if diff.days < 1:
                req2 = loads(get('https://api.github.com/repos/' +
                            organization + '/' + req[i]['name'] +
                            '/commits?since=' + yesterday).text)
                if len(req2) > 0:
                    self.msg += '\n\nName: ' + str(req[i]['name'])
                    self.msg += '\nURL repository: ' + str(req[i]['html_url'])
                    self.msg += '\n# of Commits: ' + str(len(req2))
                    commit_count += len(req2)
                    repo_count += 1
        
        if commit_count > 0:
            self.msg = "Repositories updated today: " + str(repo_count) + " with " + str(commit_count) + " commits!" + self.msg
        else:
            self.msg = "No repositories were updated today."
        self.msg += "\nt = " + str(int(time() - tempo)) +  "segundos"
        return self.msg


if __name__ == "__main__":
    arg = GitHub()