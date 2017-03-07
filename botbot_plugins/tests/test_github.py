import pytest
from mock import patch, call
import requests
from botbot_plugins.base import DummyApp
from botbot_plugins.plugins import github


class FakeResponse(object):
    """Dummy response from GitHub"""
    status_code = 200
    json = lambda x: {
        'title': 'PICARD-XX: Test YYY',
        'html_url': 'https://github.com/metabrainz/picard/pulls/1'
    }


@pytest.fixture
def app():
    dummy_app = DummyApp(test_plugin=github.Plugin())
    dummy_app.set_config('github', {'organization': 'metabrainz'})
    return dummy_app


def test_github(app):
    # patch requests.get so we don't need to make a real call to GitHub
    with patch.object(requests, 'get') as mock_get:
        mock_get.return_value = FakeResponse()
        stored = app.respond("@gh:P=picard")
        assert stored == ["Successfully stored the repo picard as P for Github lookups"]
        responses = app.respond("I'm working on gh:P#1 today")
        mock_get.assert_called_with(
            'https://api.github.com/repos/metabrainz/picard/pulls/1',
            auth=None)
        expected = ("PICARD-XX: Test YYY: "
                    "https://github.com/metabrainz/picard/pulls/1")
        assert responses == [expected]
