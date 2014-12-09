import os
from django.contrib.auth.models import User
from os import path
from dulwich import repo
from dulwich.client import HttpGitClient
from octonyan.models import Repository, Analysis
from shutil import rmtree

__author__ = 'akhmetov'
from analysis.celery import app
from octonyan.utils import check_source

@app.task
def re_statistic(path):
    """
    method for static
    :return: None
    """
    return check_source(path)


@app.task
def create_repo(repository_url, dir_name, to_fetch, user=None):
    """Check on valid state repository url and try download it into."""

    SETTINGS_DIR = os.path.dirname(__file__)
    PROJECT_PATH = os.path.join(SETTINGS_DIR, os.path.pardir)
    PROJECT_PATH = os.path.abspath(PROJECT_PATH)
    MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media')
    REPOS_PATH = os.path.join(MEDIA_ROOT, "repos")
    pth = path.join(REPOS_PATH, dir_name)
    if not path.exists(pth):
        rep = Repository()
        try:
            if not Repository.objects.filter(url=repository_url).exists():
                local = repo.Repo.init(pth, mkdir=True)
                client = HttpGitClient(repository_url)
                remote_refs = client.fetch(
                    to_fetch, local,
                    determine_wants=local.object_store.determine_wants_all,
                )
                local["HEAD"] = remote_refs["HEAD"]
                local._build_tree()
                rep.repo_dir_name = pth
                rep.title = dir_name
                rep.url = repository_url
                rep.user = user if user else User.objects.first()
                rep.save()
                analysis = Analysis()
                analysis.commit_hash = local['HEAD'].id
                analysis.repo = rep
                analysis.pep8_average, analysis.pep257_average, analysis.total_docstr_cover = re_statistic(pth)
                analysis.pep8_average = int(round(analysis.pep8_average*10000))
                analysis.pep257_average = int(round(analysis.pep257_average*10000))
                analysis.total_docstr_cover = int(round(analysis.total_docstr_cover*10000))
                analysis.commit_author = user if user else User.objects.first()
                analysis.save()
                rep.last_cheking_commit = analysis
                rep.save()
        except Exception:
            rmtree(pth)
            rep.delete()
            raise RuntimeError("Something went wrong.")

