from django import forms
import re
from shutil import rmtree
from os import path
from django.conf import settings
from dulwich.client import HttpGitClient
from dulwich import repo
from analysis.tasks import create_repo


class InitRepositoryForm(forms.Form):

    """Basic repository url form"""
    repository_url = forms.CharField(
        required=True, max_length=150, min_length=20)

    @staticmethod
    def parse_http_url(repo_url):
        """Parsing full repo url.

        Return:
          to_fetch -- string to git client, format *.git
          dir_name -- media_path/repository_name without git extension
        """
        r = re.compile("/[\w-]+.git")
        url = r.search(repo_url)
        if url:
            url = url.group()
            to_fetch = url.lstrip('/')
            dir_name = to_fetch.replace(".git", "")
            repo_url = repo_url.split("/")[:-1]
            repo_url = "/".join(repo_url)

            return (repo_url, to_fetch, dir_name)

        raise forms.ValidationError("Incorect url to repository.")

    def clean_repository_url(self):
        """Check on valid state repository url and try download it into."""
        checker = re.compile("htt(p|ps)://\w.+/\w.+/\w.+.git")
        repository_url = self.cleaned_data["repository_url"]
        if not checker.match(repository_url):
            raise forms.ValidationError("Incorrect url to repository.")

        repository_url, to_fetch, dir_name = InitRepositoryForm.parse_http_url(
            repository_url)
        self.cleaned_data['to_fetch'] = to_fetch
        self.cleaned_data['dir_name'] = dir_name

        return repository_url