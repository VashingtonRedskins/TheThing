#!/usr/bin/python

from django.shortcuts import render
from django.conf import settings
from django.views.generic.edit import FormView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import login
from django.dispatch import receiver


from os import path
from os import listdir
from datetime import datetime

from dulwich import repo, diff_tree
from difflib import unified_diff
import operator

from octonyan import utils
from octonyan.forms import InitRepositoryForm

from analysis.tasks import re_statistic

from registration.backends.default.views import ActivationView
from registration.signals import user_activated


@receiver(user_activated)
def login_on_activation(sender, user, request, **kwargs):
    """Logs in the user after activation"""
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request, user)


class OctonyanActivationView(ActivationView):

    """ Override success_url by ActivationView. """

    def get_success_url(self, request, user):
        """ Redirect to dashboard after activation."""
        return "/octonyan/"


class InitRepositoryView(FormView):

    """Getting form to add new repository"""

    template_name = "octonyan/init_form.html"
    form_class = InitRepositoryForm
    success_url = "/octonyan/"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(FormView, self).dispatch(*args, **kwargs)


@login_required
def repository(request, repo_dir):
    """View basic commits information"""
    pth = path.join(settings.REPOS_PATH, repo_dir)
    repository = repo.Repo(pth)
    walker = repository.get_graph_walker()
    committers = dict()
    history = []
    cset = walker.next()

    while cset is not None:
        commit = repository.get_object(cset)
        committers[commit.author] = \
            committers.get(commit.author, 0) + 1
        data = (
            commit.id,
            commit.author,
            datetime.fromtimestamp(commit.commit_time).strftime(
                "%a %b %d %H:%M:%S %Y"),
            commit.message,
        )
        history.append(data)
        cset = walker.next()

    sorted_commiters = sorted(
        committers.items(), key=operator.itemgetter(1), reverse=True)

    context = {
        "committers": sorted_commiters,
        "history": history,
        "repo": repo_dir,
    }

    return render(
        request,
        "octonyan/detail.html",
        context
    )


# TODO refactoring and change
@login_required
def detail_commit_view(request, repo_dir, commit_id, files_extenshion=None):
    """Return changes make in current commit

    data -- include blocks code of each modify files.

    """
    pth = path.join(settings.REPOS_PATH, repo_dir)
    repository = repo.Repo(pth)
    data = []
    # used encode('latin-1') below to solve some problem with unicode
    # and bytestring
    commit = repository[commit_id.encode('latin-1')]
    if len(commit.parents) == 0:
        parent = None
    else:
        parent = repository[commit.parents[0]].tree

    delta = diff_tree.tree_changes(repository, parent, commit.tree)

    for item in delta:
        block = []
        old = ""
        if item.old.sha:
            old = repository[item.old.sha].data.split("\n")

        new = repository[item.new.sha].data.split("\n")
        for line in unified_diff(old, new):
            block.append(line)

        data.append(
            (item.old.path, item.new.path, block)
        )

    return render(request, "octonyan/commit_info.html", {"data": data})


# TODO refactoring and change
@login_required
def analysis(request, repo_dir, commit_id):
    pth = path.join(settings.REPOS_PATH, repo_dir)
    repository = repo.Repo(pth)
    # used encode('latin-1') below to solve some problem with unicode
    # and bytestring
    repository["HEAD"] = commit_id.encode('latin-1')
    repository._build_tree()
    print pth
    report = utils.check_source(pth)

    return render(request, "octonyan/analysis.html",
                  {"report": report, "repo": repo_dir})


# TODO change when will complete registration
@login_required
def index(request):
    """View all current repository"""
    r = []
    # call celery method by async
    re_statistic.delay()
    if path.exists(settings.REPOS_PATH):
        for d in listdir(settings.REPOS_PATH):
            print d
            r.append(d)
    return render(request, "octonyan/index.html", {"repos": r})
