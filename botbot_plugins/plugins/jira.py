import requests
import json
from urlparse import urljoin
from .. import config
from ..base import BasePlugin
from ..decorators import listens_to_all, listens_to_mentions



class Config(config.BaseConfig):
    jira_link = config.Field(help_text="Jira Link, eg: 'https://tickets.metabrainz.org'")
    rest_api_suffix = config.Field(help_text="Suffix for the Jira REST API, eg: 'rest/api/2/project'", default="rest/api/2/project")

class Plugin(BasePlugin):
    """
    Jira issue lookup

    Returns the description of a Jira Issue

        jira:{{projectname}}-{{issuenumber}}
    """
    config_class = Config

    @listens_to_all(ur'(?:.*)\b(?P<project>\w+)-(?P<issue>\d+)\b(?:.*)')
    def issue_lookup(self, line, project, issue):
        """Lookup a specified jira issue

            Usage:
                Just mention the issue by its {{ISSUENAME}}
                Eg:
                    Can you please checkup on PROJECT-123
        """

        api_url = urljoin(self.config['jira_link'], self.config['rest_api_suffix'])
        projects = json.loads(self.retrieve('projects'))
        if project.upper() in projects:

            issue_url = urljoin(api_url,"issue/{}-{}".format(project.upper(),(issue)))
            response = requests.get(issue_url)
            if response.status_code == 200:
                response_text = json.loads(response.text)
                name = response_text['key']
                desc = response_text['fields']['summary']
                return_url = urljoin(self.config['jira_link'],"projects/{}/issues/{}".format(project,name))
                return "{}: {}\n{}".format(name,desc,return_url)
            else:
                return "Th' servers be not reachable matey, give a go' again later" 

    @listens_to_mentions(ur'UPDATE:JIRA')
    def update_projects(self, line):
        """Updates projects list

            Usage:
                Ping the botbot with the command:
                UPDATE:JIRA
        """

        api_url = urljoin(self.config['jira_link'], self.config['rest_api_suffix'])
        project_url = urljoin(api_url, 'project')
        response = requests.get(project_url)
        if response.status_code == 200:
            projects = [project['key'] for project in json.loads(response.text)]
            self.store('projects', json.dumps(projects))
            return "Successfully updated projects list"
        return "Could not update projects list"
