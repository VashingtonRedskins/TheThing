import os
from django.contrib.auth.models import User
from os import path
from dulwich import repo
from dulwich.client import HttpGitClient
from octonyan.dao import is_rep, get_by_dir_name
from octonyan.models import Repository, Commit, UserRepository, \
    CommitterRepository
from shutil import rmtree
from datetime import datetime
import operator

__author__ = 'akhmetov'
from analysis.celery import app
from octonyan.utils import check_source

SETTINGS_DIR = os.path.dirname(__file__)
PROJECT_PATH = os.path.join(SETTINGS_DIR, os.path.pardir)
PROJECT_PATH = os.path.abspath(PROJECT_PATH)
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media')
REPOS_PATH = os.path.join(MEDIA_ROOT, "repos")


@app.task
def re_statistic(path):
    """
    method for static
    :return: None
    """
    return check_source(path)


def create_commit(id_commit, rep, msg=None, author=None,
                  create_date=None):
    commit = Commit()
    commit.id_commit = id_commit
    commit.repo = rep
    commit.pep8_average, commit.pep257_average, commit.total_docstr_cover = re_statistic(
        rep.repo_dir_name)
    commit.pep8_average = int(round(commit.pep8_average * 10000))
    commit.pep257_average = int(round(commit.pep257_average * 10000))
    commit.total_docstr_cover = int(
        round(commit.total_docstr_cover * 10000))
    commit.msg = msg or ''
    commit.author = author or ''
    commit.create_date = create_date
    commit.save()
    return commit


@app.task
def analysis(id_commit, dir_name):
    rep = get_by_dir_name(dir_name)
    if rep:
        rep.last_cheking_commit = create_commit(id_commit, rep)
        rep.save()


@app.task
def create_repo(repository_url, dir_name, to_fetch, user):
    """Check on valid state repository url and try download it into."""

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
                rep.last_check = create_commit(local['HEAD'].id, rep)
                rep.save()
                create_analysis(dir_name)
        except Exception:
            rmtree(pth)
            rep.delete()
            raise RuntimeError("Something went wrong.")
    else:
        rep = get_by_dir_name(dir_name)
        if rep:
            UserRepository(repo=rep, user=user).save()


@app.task
def create_analysis(dir_name):
    rep = get_by_dir_name(dir_name)
    pth = path.join(REPOS_PATH, dir_name)
    repository = repo.Repo(pth)
    walker = repository.get_graph_walker()
    committers = dict()
    cset = walker.next()

    while cset is not None:
        commit = repository.get_object(cset)
        committers[commit.author] = committers.get(commit.author, 0) + 1
        cset = walker.next()
        create_commit(
            commit.id, rep, msg=commit.message,
            author=commit.author,
            create_date=datetime.fromtimestamp(commit.commit_time)
        )


    for committer, count in committers.iteritems():
        CommitterRepository(committer=committer, count=count, repo=rep).save()



