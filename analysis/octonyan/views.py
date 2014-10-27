#!/usr/bin/python

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from os.path import join, exists
from os import listdir
from django.conf import settings
from dulwich import repo, diff_tree
from dulwich.client import HttpGitClient
from shutil import rmtree
from datetime import datetime
from difflib import unified_diff


# TODO add the ability to access by ssh client
def init_repo(request):
    """Clone git repository by url and register it
    if doesn't exist. Return state about doing work.

    repo_url -- entering repo https url
    status_msg -- indicate state with init repository
    """
    if request.POST:
        status_msg = "Repository already exist"
        repo_url = request.POST["repo_url"].split('/')
        to_fetch = repo_url[-1]
        dir = to_fetch.split('.')[0]
        repo_url = "/".join(repo_url[:-1])
        path = join(settings.REPOS_PATH, dir)

        if not exists(path):
            try:
                local = repo.Repo.init(path, mkdir=True)
                client = HttpGitClient(repo_url)
                remote_refs = client.fetch(
                    to_fetch, local,
                    determine_wants=local.object_store.determine_wants_all,
                )
                local["HEAD"] = remote_refs["HEAD"]
                local._build_tree()

                return HttpResponseRedirect(reverse("octonyan:index"))

            except Exception:
                rmtree(path)
                status_msg = "Something went wrong."

        return render(request, "octonyan/init_form.html",
                      {"status_message": status_msg})

    return render(request, "octonyan/init_form.html")


# TODO add content to view changes files bettwen commit
# and parrent commit or imp featur such as git blame [file]
def repository(request, repo_dir):
    """View basic commits information"""

    path = join(settings.REPOS_PATH, repo_dir)
    repository = repo.Repo(path)
    walker = repository.get_graph_walker()
    committers = dict()
    history = []
    cset = walker.next()
    # print patch.write_tree_diff(
    #     sys.stdout, repository.object_store, prev.tree, cur.tree)

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

    context = {
        "committers": committers,
        "history": history,
        "repo": repo_dir,
    }

    return render(
        request,
        "octonyan/detail.html",
        context
    )


# FIXME first commit don't show because it doesn't have parents
# raise IndexError and problem with TypeError are raising in some commits
def detail_commit_view(request, repo_dir, commit_id, files_extenshion=None):
    """Return changes make in current commit

    data -- include blocks code of each modify files
    """
    path = join(settings.REPOS_PATH, repo_dir)
    repository = repo.Repo(path)
    data = []
    # used encode('latin-1') below to solve some problem with unicode
    # and bytestring
    commit = repository[commit_id.encode('latin-1')]
    parent = repository[commit.parents[0]]
    delta = diff_tree.tree_changes(repository, parent.tree, commit.tree)

    for item in delta:
        block = []
        old = repository[item.old.sha].data.split("\n")
        new = repository[item.new.sha].data.split("\n")
        for line in unified_diff(old, new):
            block.append(line)

        data.append(
            (item.old.path, item.new.path, block)
        )

    return render(request, "octonyan/commit_info.html", {"data": data})


# TODO change when will complete registration
def index(request):
    """View all current repository"""

    r = []
    for d in listdir(settings.REPOS_PATH):
        r.append(d)
    return render(request, "octonyan/index.html", {"repos": r})
