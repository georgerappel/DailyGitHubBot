#!/usr/bin/env python
# -*- coding:utf-8 -*-

from datetime import datetime, timedelta
from json import loads
from requests import get
import logging
import utils


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
        if not utils.is_username_valid(organization):
            return "Invalid username"

        self.msg = ""
        self.msg += '{0} Repositories for '.format('\U0001F5C4') \
                    + '[{0}](https://github.com/{0}):\n\n'.format(organization)
        req = loads(get('https://api.github.com/orgs/' + organization + '/repos' + self.url_parameters()).text)
        for i in range(len(req)):
            # Name with URL
            self.msg += '\n\n[' + escape_to_markdown(str(req[i]['name'])) + '](' + str(req[i]['html_url']) + ')'
            # Description on the second line
            self.msg += '\n\U0001F4C4 ' + escape_to_markdown(str(req[i]['description']))

        if len(req) == 0:
            self.msg += "No repositories found."

        return self.msg

    # Count commits today for an organization
    def get_org_today(self, organization):
        if not utils.is_username_valid(organization):
            return "Invalid username"

        self.msg = ""
        self.msg += '{0} Today\'s updates for '.format('\U0001F5C4') \
                    + '[{0}](https://github.com/{0}):\n\n'.format(organization)
        commit_count = 0
        repo_count = 0
        today = datetime.now()
        yesterday = (today - timedelta(1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        url = 'https://api.github.com/orgs/' + organization + '/repos' + self.url_parameters()
        req = loads(get(url).text)

        # Handles case where there's an API error
        try:
            if req['message'] is not None:
                logging.getLogger(__name__).error("API ERROR /today: " + req['message'])
                return "Unable to get updates for this organization at this time."
        except:
            pass

        repo_range = len(req) if len(req) <= 20 else 20  # Limita a 20 repositórios
        for i in range(repo_range):
            pushed_at = datetime.strptime(req[i]['pushed_at'], "%Y-%m-%dT%H:%M:%SZ")
            diff = datetime.now() - pushed_at
            if diff.days < 1:
                req2 = loads(get('https://api.github.com/repos/' + organization + '/' + req[i]['name']
                                 + '/commits?since=' + yesterday).text)
                if len(req2) > 0:
                    self.msg += '\n' + escape_to_markdown(str(req[i]['name'])) + ': ' + str(len(req2)) + ' commits'
                    commit_count += len(req2)
                    repo_count += 1

        if commit_count > 0:
            self.msg = "*" + str(repo_count) + " repos updated with " + str(commit_count) + " commits!*\n" + self.msg
        else:
            self.msg = self.msg + "No repositories were updated today."

        return self.msg, commit_count


# Used to escape special characters in usernames or texts that break the markdown support of Telegram
def escape_to_markdown(text):
    new_text = text
    new_text = new_text.replace("_", "\\_")
    new_text = new_text.replace("*", "\\*")
    new_text = new_text.replace("[", "")
    new_text = new_text.replace("<<", "")
    return new_text
