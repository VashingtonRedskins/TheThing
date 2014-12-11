import os
from os import path
from dulwich import repo
from dulwich.client import HttpGitClient
from octonyan.dao import is_rep, get_by_dir_name, get_head_commit
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
                  create_date=None, another_commit=None):
    commit = Commit()
    commit.id_commit = id_commit
    commit.repo = rep
    commit.pep8_average, commit.pep257_average, commit.total_docstr_cover = \
        re_statistic(rep.repo_dir_name)
    commit.pep8_average = int(round(commit.pep8_average * 10000))
    commit.pep257_average = int(round(commit.pep257_average * 10000))
    commit.total_docstr_cover = int(
        round(commit.total_docstr_cover * 10000))
    commit.msg = msg or ''
    commit.author = author or ''
    commit.create_date = create_date
    if another_commit:
        commit.pep8 = commit.pep8_average - another_commit.pep8_average
        commit.pep257 = commit.pep257_average - another_commit.pep257_average
        commit.total = commit.total_docstr_cover - another_commit.total_docstr_cover
    else:
        commit.pep8 = commit.pep8_average
        commit.pep257 = commit.pep257_average
        commit.total = commit.total_docstr_cover
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
    flag = 0
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
                rep.url = '/'.join((repository_url, dir_name))
                rep.save()
                flag = 1
                UserRepository(repo=rep, user=user).save()
                rep.last_check = get_head_commit(rep)
                rep.save()
                create_analysis(dir_name)
        except Exception:
            rmtree(pth)
            if flag == 1:
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
    committers = {}
    cset = walker.next()
    cmmt = None
    while cset is not None:
        commit = repository.get_object(cset)
        repository["HEAD"] = cset.encode('latin-1')
        repository._build_tree()
        if not commit.author in committers.keys():
            committers[commit.author] = {
                "count": 0,
                "pep8": 0.0,
                "pep257": 0.0,
                "doccover": 0.0
            }
        pep8_av, pep257_av, doccover = check_source(pth)
        committers[commit.author]["count"] += 1
        committers[commit.author]["pep8"] += pep8_av
        committers[commit.author]["pep257"] += pep257_av
        committers[commit.author]["doccover"] += doccover

        cset = walker.next()
        cmmt = create_commit(
            commit.id, rep, msg=commit.message,
            author=commit.author,
            create_date=datetime.fromtimestamp(commit.commit_time),
            another_commit=cmmt
        )

    for committer, stat in committers.items():
        count = stat["count"]
        CommitterRepository(
            committer=committer,
            count=count,
            repo=rep,
            pep8_average=round(stat["pep8"] / count, 3),
            pep257_average=round(stat["pep257"] / count, 3),
            docstr_cover_average=round(stat["doccover"] / count, 3),
        ).save()
