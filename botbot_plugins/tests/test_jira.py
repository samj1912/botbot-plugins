import pytest
import json
from mock import patch, call
import requests
from botbot_plugins.base import DummyApp
from botbot_plugins.plugins import jira


class FakeProjectResponse(object):
    """Dummy response from JIRA"""
    status_code = 200
    text = json.dumps([{'key': 'TEST'}])


class FakeUserResponse(object):
    """Dummy response from JIRA"""
    def __init__(self, key, summary):
        self.status_code = 200
        self.text = json.dumps({'key': key, 'fields': {'summary': summary}})


def patched_get(*args, **kwargs):
    if args[0] == "https://tickets.test.org/rest/api/2/project":
        return FakeProjectResponse()
    elif args[0] == "https://tickets.test.org/rest/api/2/issue/TEST-123":
        return FakeUserResponse("TEST-123", "Testing JIRA plugin")
    elif args[0] == "https://tickets.test.org/rest/api/2/issue/TEST-234":
        return FakeUserResponse("TEST-234", "Something is being tested again")
    else:
        return FakeUserResponse("TEST-000", "Default Test")


@pytest.fixture
def app():
    dummy_app = DummyApp(test_plugin=jira.Plugin())
    dummy_app.set_config('jira', {'jira_url': 'https://tickets.test.org', 'bot_name': 'testbot'})
    return dummy_app


def test_jira(app):
    # patch requests.get so we don't need to make a real call to Jira

    # Test project retrival
    with patch.object(requests, 'get') as mock_get:
        mock_get.side_effect = patched_get
        responses = app.respond("@UPDATE:JIRA")
        mock_get.assert_called_with(
            'https://tickets.test.org/rest/api/2/project')
        assert responses == ["Successfully updated projects list"]

    # Test appropriate response
    with patch.object(requests, 'get') as mock_get:
        mock_get.side_effect = patched_get
        responses = app.respond("I just assigned TEST-123 to testuser")
        mock_get.assert_called_with(
            'https://tickets.test.org/rest/api/2/issue/TEST-123')
        assert responses == ["TEST-123: Testing JIRA plugin https://tickets.test.org/browse/TEST-123"]

    # Test responside when issue is mentioned as part of url
    with patch.object(requests, 'get') as mock_get:
        mock_get.side_effect = patched_get
        responses = app.respond("Check out https://tickets.test.org/browse/TEST-123")
        mock_get.assert_called_with(
            'https://tickets.test.org/rest/api/2/issue/TEST-123')
        assert responses == ["TEST-123: Testing JIRA plugin"]


def test_jira_multiple(app):

    # Test multiple issues in a single message
    with patch.object(requests, 'get') as mock_get:
        mock_get.side_effect = patched_get
        responses = app.respond("I think TEST-123 and TEST-234 are related")
        expected_calls = [call('https://tickets.test.org/rest/api/2/issue/TEST-123'), call('https://tickets.test.org/rest/api/2/issue/TEST-234')]
        expected_response = ["TEST-123: Testing JIRA plugin https://tickets.test.org/browse/TEST-123", "TEST-234: Something is being tested again https://tickets.test.org/browse/TEST-234"]
        assert mock_get.mock_calls == expected_calls
        assert responses[0].split('\n') == expected_response
