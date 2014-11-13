from django import forms
import re
from shutil import rmtree
from os import path
from django.conf import settings
from dulwich.client import HttpGitClient
from dulwich import repo


class AddingRepositoryForm(forms.Form):

    """Basic repository url form"""
    repository_url = forms.CharField(
        required=True, max_length=150, min_length=20)

    @staticmethod
    def parse_url(repo_url):
        """Parsing full repo url.

        Return:
          to_fetch -- string to git client, format *.git

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

        raise forms.ValidationError("Incorent url to repository")

    def clean_repository_url(self):
        """Check on valid state repository url and try download it."""
        checker = re.compile("htt(p|ps)://\w.+/\w.+/\w.+.git")
        repository_url = self.cleaned_data["repository_url"]
        print "first repo url", repository_url
        if not checker.match(repository_url):
            raise forms.ValidationError("Incorent url to repository")

        repository_url, to_fetch, dir_name = AddingRepositoryForm.parse_url(
            repository_url)

        print "R_URL", repository_url
        print "to_fetch", to_fetch
        print "dir name", dir_name
        pth = path.join(settings.REPOS_PATH, dir_name)
        if not path.exists(pth):
            try:
                local = repo.Repo.init(pth, mkdir=True)
                client = HttpGitClient(repository_url)
                remote_refs = client.fetch(
                    to_fetch, local,
                    determine_wants=local.object_store.determine_wants_all,
                )
                local["HEAD"] = remote_refs["HEAD"]
                local._build_tree()

            except Exception, e:
                "<<<<<<<<<<<<<<<Exception log"
                print str(e)
                "<<<<<<<<<<<<<<<Exception log"
                rmtree(pth)
                raise forms.ValidationError("Something went wrong.")
