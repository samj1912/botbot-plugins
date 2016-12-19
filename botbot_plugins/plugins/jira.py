import requests
import json
import re
from urlparse import urljoin
from .. import config
from ..base import BasePlugin, DummyLine
from ..decorators import listens_to_all, listens_to_mentions



class Config(config.BaseConfig):
    jira_url = config.Field(help_text="JIRA Link, eg: 'https://tickets.metabrainz.org'")
    rest_api_suffix = config.Field(help_text="Suffix for the JIRA REST API, eg: 'rest/api/2/project'", default="rest/api/2/project")
    bot_name = config.Field(help_text="Name of your bot, eg: BrainzBot")

class Plugin(BasePlugin):
    """
    JIRA issue lookup

    Returns the description of a JIRA Issue

        jira:{{projectname}}-{{issuenumber}}
    """
    config_class = Config
    
    @listens_to_all(ur'(?:.*)\b(?P<project>\w+)-(?P<issue>\d+)\b(?:.*)')
    def issue_lookup(self, line, project, issue):
        """
        Lookup a specified JIRA issue

        Usage:
            Just mention the issue by its {{ISSUENAME}}
            Eg:
                Can you please checkup on PROJECT-123
        """

        if line.user != self.config['bot_name']:
            api_url = urljoin(self.config['jira_url'], self.config['rest_api_suffix'])
            projects = json.loads(self.retrieve('projects'))

            if project.upper() in projects:
                issue_url = urljoin(api_url,"issue/{}-{}".format(project.upper(), issue))
                response = requests.get(issue_url)

                if response.status_code == 200:
                    response_text = json.loads(response.text)
                    name = response_text['key']
                    desc = response_text['fields']['summary']

                    # Only post URL if issue isn't already mentioned as part of one
                    if re.search(ur'(http)(\S*)/({})\b'.format(name), line.text):
                        return "{}: {}".format(name, desc)

                    return_url = urljoin(self.config['jira_url'], "browse/{}".format(name))
                    return "{}: {} {}".format(name, desc, return_url)

    @listens_to_mentions(ur'(.*)\bUPDATE:JIRA')
    def update_projects(self, line):
        """
        Updates projects list on mentioning the bot with the command

        Usage:
            Ping the bot with the command:
            UPDATE:JIRA
        """
        api_url = urljoin(self.config['jira_url'], self.config['rest_api_suffix'])
        project_url = urljoin(api_url, 'project')
        response = requests.get(project_url)

        if response.status_code == 200:
            projects = [project['key'] for project in json.loads(response.text)]
            self.store('projects', json.dumps(projects))
            return "Successfully updated projects list"

        return "Could not update projects list"