import os
from django.contrib.auth.models import User
from os import path
from dulwich import repo
from dulwich.client import HttpGitClient
from octonyan.dao import is_rep, get_by_dir_name
from octonyan.models import Repository, Commit, UserRepository
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


def create_analysis(commit_hash, rep):
    commit = Commit()
    commit.commit_hash = commit_hash
    commit.repo = rep
    commit.pep8_average, commit.pep257_average, commit.total_docstr_cover = re_statistic(
        rep.repo_dir_name)
    commit.pep8_average = int(round(commit.pep8_average * 10000))
    commit.pep257_average = int(round(commit.pep257_average * 10000))
    commit.total_docstr_cover = int(
        round(commit.total_docstr_cover * 10000))
    commit.save()
    return commit


@app.task
def analysis(commit_hash, repo_dir, user):
    rep = get_by_dir_name(repo_dir)
    if rep:
        rep.last_cheking_commit = create_analysis(commit_hash, rep)
        rep.save()


@app.task
def create_repo(repository_url, dir_name, to_fetch, user):
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
            if not is_rep(repository_url):
                local = repo.Repo.init(pth, mkdir=True)
                client = HttpGitClient(repository_url)
                remote_refs = client.fetch(
                    to_fetch, local,
                    determine_wants=local.object_store.determine_wants_all,
                )
                local["HEAD"] = remote_refs["HEAD"]
                local._build_tree()
                rep.repo_dir_name = pth
                rep.dir_name = dir_name
                rep.url = repository_url
                rep.save()
                UserRepository(repo=rep, user=user).save()
                rep.last_check = create_analysis(local['HEAD'].id, rep)
                rep.save()
        except Exception:
            rmtree(pth)
            rep.delete()
            raise RuntimeError("Something went wrong.")
    else:
        UserRepository(repo=get_by_dir_name(dir_name), user=user).save()
