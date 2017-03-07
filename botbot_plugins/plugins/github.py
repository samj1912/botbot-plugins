import requests
from ..base import BasePlugin
from .. import config
from ..decorators import listens_to_all, listens_to_mentions


class Config(config.BaseConfig):
    organization = config.Field(help_text="GitHub organization")
    repo = config.Field(required=False,
                        help_text="GitHub repository name")
    user = config.Field(
        required=False,
        help_text="GitHub username to connect to API (for private repos)")
    password = config.Field(
        required=False,
        help_text="GitHub password to connect to API (for private repos)")


class Plugin(BasePlugin):
    """
    Github pull lookup

    Looking for the url of an pull or a list of pulls:

    To store an abbreviation for a repo use

    @gh:abbreviation:repo_name

    To retrieve a PR simply use:

    gh:abbreviation#PR_number

    Note: The lookup is limited to 5 issues.
    """
    url = "https://api.github.com/repos"
    config_class = Config

    @listens_to_mentions(ur'(?:.*)\b(?:GH|gh):(?P<abbreviation>[\w\-\_]+)=(?P<repo>[\w\-\_]+)')
    def store_abbreviation(self, line, abbreviation, repo):
        """Store an abbreviation for future PR lookups"""
        self.store(abbreviation, repo)
        return "Successfully stored the repo {} as {} for Github lookups".format(repo, abbreviation)

    @listens_to_all(ur'(?:.*)\b(?:GH|gh):(?P<repo_abbreviation>[\w\-\_]+)#?(?P<pulls>\d+(?:,\d+)*)\b(?:.*)')
    def issue_lookup(self, line, repo_abbreviation, pulls):
        """Lookup an specified repo pulls"""
        # pulls can be a list of pulls separated by a comma
        pull_list = [i.strip() for i in pulls.split(",")]
        repo = self.retrieve(repo_abbreviation)
        if not repo:
            return
        response_list = []
        for pull in pull_list[:5]:
            api_url = "/".join([self.url, self.config['organization'],
                                repo, "pulls", pull])
            response = requests.get(api_url, auth=self._get_auth())
            if response.status_code == 200:
                resp = u'{title}: {html_url}'.format(**response.json())
                response_list.append(resp)
            else:
                resp = u"Sorry I couldn't find pull #{0} in {1}/{2}".format(
                    pull, self.config['organization'], repo)
                response_list.append(resp)

        return ", ".join(response_list)

    def _get_auth(self):
        """Return user credentials if they are configured"""
        if self.config['user'] and self.config['password']:
            return (self.config['user'], self.config['password'])
        return None
