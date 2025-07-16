import unittest
from parameterized import parameterized
from unittest.mock import patch, PropertyMock, Mock
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.get_json")
    def test_org(self, org_name, mock_get_json):
        fake_response = {"login": org_name, "repos_url": f"https://api.github.com/orgs/ {org_name}/repos"}
        mock_get_json.return_value = fake_response

        client = GithubOrgClient(org_name)
        result = client.org

        expected_url = f"https://api.github.com/orgs/ {org_name}"
        mock_get_json.assert_called_once_with(expected_url)
        self.assertEqual(result, fake_response)

    def test_public_repos_url(self):
        mock_org_payload = {
            "repos_url": "https://api.github.com/orgs/google/custom_repos "
        }

        with patch("client.GithubOrgClient.org", new_callable=PropertyMock) as mock_org:
            mock_org.return_value = mock_org_payload

            client = GithubOrgClient("google")
            result = client._public_repos_url

            expected_url = mock_org_payload["repos_url"]
            self.assertEqual(result, expected_url)

    @patch("client.get_json")
    def test_public_repos(self, mock_get_json):
        fake_payload = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
            {"name": "repo3", "license": {"key": "mit"}},
        ]
        mock_get_json.return_value = fake_payload

        with patch("client.GithubOrgClient._public_repos_url", new_callable=PropertyMock) as mock_repos_url:
            mock_repos_url.return_value = "https://api.github.com/orgs/google/repos "

            client = GithubOrgClient("google")
            result = client.public_repos(license="mit")

            expected_repos = ["repo1", "repo3"]
            self.assertEqual(result, expected_repos)
            mock_repos_url.assert_called_once()
            mock_get_json.assert_called_once_with("https://api.github.com/orgs/google/repos ")

    @parameterized.expand([
        # Matching license
        ({"license": {"key": "my_license"}}, "my_license", True),
        # Non-matching license
        ({"license": {"key": "other_license"}}, "my_license", False),
        # Missing license key in repo
        ({"license": {}}, "my_license", False),
        # No license field in repo
        ({}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)